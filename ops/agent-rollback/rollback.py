#!/usr/bin/env python3
"""
Name:     ops/agent-rollback/rollback.py  (SCGOE-95 OPS-1, controls C1-C5, C7)
Purpose:  Independent, verified rollback of an Agentforce activation window.
          Runs on a GitHub Actions runner (C2), signs in with its own JWT
          integration user (C1), and fails TOWARDS rollback (C3):
            1. activate the safe version first, never gated on a read,
            2. read back BotVersion and confirm safe Active / others Inactive,
            3. retry with back-off until confirmed or a person takes over,
            4. remove the temporary grants recorded in the window file and
               turn "Administrators Can Log in as Any User" off, each read back,
            5. escalate (C5) after the hard limit, every escalation interval.
          Every CLI call is logged with UTC time, exit code, stdout and stderr,
          after redaction (C4). Alerts go to one GitHub issue per window (C5);
          GitHub e-mails the people it mentions and the repository watchers.

Modes:    precheck  R0: sign in, read versions, check the window file, alert "armed".
          window    precheck, wait until the deadline, then rollback.
          rollback  rollback now.
          backstop  if no window is open, make sure the safe version is the
                    Active one (scheduled run from the default branch).
History:  1.0  Revecast Orchestrate  27/11/2026  Created  OPS-1 rebuild
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

# ---------------------------------------------------------------- settings
ENV = os.environ
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # SFDX project folder
ALIAS = 'agent-rollback'
MAX_WINDOW_MINUTES = 90                   # C7: maximum window, enforced here
# Back-off between rollback attempts, in seconds (C3.3); the last value repeats.
BACKOFF = [int(x) for x in ENV.get('ROLLBACK_BACKOFF', '60,120,300,600').split(',')]
HARD_LIMIT_SECONDS = int(ENV.get('ROLLBACK_HARD_LIMIT_SECONDS', str(30 * 60)))      # C3.5
ESCALATE_EVERY_SECONDS = int(ENV.get('ROLLBACK_ESCALATE_EVERY_SECONDS', str(10 * 60)))
GIVE_UP_SECONDS = int(ENV.get('ROLLBACK_GIVE_UP_SECONDS', str(150 * 60)))  # before the job timeout
LOG_DIR = ENV.get('ROLLBACK_LOG_DIR', os.path.join(ROOT, 'rollback-logs'))
SF = ENV.get('ROLLBACK_SF', 'sf')
CLI_TIMEOUT = int(ENV.get('ROLLBACK_CLI_TIMEOUT', '300'))


def now():
    return dt.datetime.now(dt.timezone.utc)


def iso(moment):
    return moment.strftime('%Y-%m-%dT%H:%M:%SZ')


# ---------------------------------------------------------------- C4 redaction
SECRET_PATTERNS = [
    re.compile(r'00D[A-Za-z0-9]{12,15}![A-Za-z0-9._\-]+'),                     # Salesforce access token / sid
    re.compile(r'(?i)(bearer\s+)[A-Za-z0-9._~+/=!\-]+'),
    re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', re.S),
    re.compile(r'(?i)("(?:access_?token|refresh_?token|accessToken|refreshToken|sid|password|clientSecret|'
               r'client_secret|assertion)"\s*:\s*")[^"]*(")'),
    re.compile(r'(?i)((?:access_token|refresh_token|sid|assertion|client_secret)=)[^&\s"]+'),
    re.compile(r'eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}'),  # JWT
    re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),                                    # GitHub tokens
]
SECRET_ENV_NAMES = ('SF_JWT_KEY', 'GITHUB_TOKEN', 'SF_CLIENT_ID')


def redact(text):
    """Remove every credential the job could ever see from text before it is saved or printed."""
    if not text:
        return text
    for name in SECRET_ENV_NAMES:
        value = ENV.get(name)
        if value and len(value) >= 8:
            text = text.replace(value, '[REDACTED:%s]' % name)
            for line in value.splitlines():          # a key pasted line by line
                if len(line.strip()) >= 16:
                    text = text.replace(line.strip(), '[REDACTED:%s]' % name)
    for pattern in SECRET_PATTERNS:
        if pattern.groups >= 2:
            text = pattern.sub(lambda m: m.group(1) + '[REDACTED]' + m.group(2), text)
        elif pattern.groups == 1:
            text = pattern.sub(lambda m: m.group(1) + '[REDACTED]', text)
        else:
            text = pattern.sub('[REDACTED]', text)
    return text


class Log:
    """C4: every event and CLI call, redacted, as JSON lines plus a readable text log."""

    def __init__(self, window_id):
        self.dir = os.path.join(LOG_DIR, window_id)
        os.makedirs(self.dir, exist_ok=True)
        self.calls = os.path.join(self.dir, 'calls.jsonl')
        self.text = os.path.join(self.dir, 'rollback.log')

    def event(self, message):
        line = '%s %s' % (iso(now()), redact(message))
        print(line, flush=True)
        with open(self.text, 'a', encoding='utf-8') as handle:
            handle.write(line + '\n')

    def call(self, record):
        record = {key: (redact(value) if isinstance(value, str) else value) for key, value in record.items()}
        record['argv'] = [redact(a) for a in record.get('argv', [])]
        with open(self.calls, 'a', encoding='utf-8') as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + '\n')


# ---------------------------------------------------------------- Salesforce CLI
class Cli:
    def __init__(self, log):
        self.log = log

    def run(self, args, label, cwd=None):
        """Run one sf command. Never raises; returns (ok, parsed_json_or_None, message)."""
        argv = [SF] + args + ['--json']
        started = now()
        env = dict(ENV)
        env.pop('SF_DISABLE_LOG_FILE', None)          # C4: keep the CLI log file on
        env['SF_SKIP_NEW_VERSION_CHECK'] = 'true'
        try:
            proc = subprocess.run(argv, cwd=cwd or ROOT, capture_output=True, text=True, timeout=CLI_TIMEOUT, env=env)
            out, err, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as expired:
            out, err, code = (expired.stdout or ''), 'TIMEOUT after %ss' % CLI_TIMEOUT, -1
            out = out.decode() if isinstance(out, bytes) else out
        except OSError as failure:
            out, err, code = '', 'could not start CLI: %s' % failure, -2
        self.log.call({'ts': iso(started), 'end': iso(now()), 'label': label, 'argv': argv,
                       'exit': code, 'stdout': out, 'stderr': err})
        parsed = None
        try:
            parsed = json.loads(out[out.index('{'):]) if '{' in out else None
        except ValueError:
            parsed = None
        ok = code == 0 and parsed is not None and parsed.get('status') == 0
        message = ''
        if not ok:
            message = (parsed or {}).get('message') or err.strip()[-400:] or out.strip()[-400:] or 'exit %s' % code
        return ok, parsed, redact(str(message))

    def login(self, username, instance_url, client_id, key_file):
        return self.run(['org', 'login', 'jwt', '--username', username, '--jwt-key-file', key_file,
                         '--client-id', client_id, '--instance-url', instance_url, '--alias', ALIAS], 'login')

    def query(self, soql, label):
        ok, parsed, message = self.run(['data', 'query', '--target-org', ALIAS, '--query', soql], label)
        return (parsed['result']['records'] if ok else None), message

    def versions(self, agent):
        records, message = self.query(
            "SELECT VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '%s'" % agent,
            'read-versions')
        if records is None:
            return None, message
        return {int(r['VersionNumber']): r['Status'] for r in records}, ''

    def activate(self, agent, version):
        return self.run(['agent', 'activate', '--api-name', agent, '--version', str(version),
                         '--target-org', ALIAS], 'activate-v%s' % version)


# ---------------------------------------------------------------- C5 alerts
class Alerts:
    """One GitHub issue per window; each event is a comment. Mentions e-mail the named people."""

    def __init__(self, log, window):
        self.log = log
        self.window = window
        self.repo = ENV.get('GITHUB_REPOSITORY')
        self.token = ENV.get('GITHUB_TOKEN')
        self.sink = ENV.get('ROLLBACK_ALERT_SINK')          # tests: write alerts to a file instead
        self.issue = None
        self.title = 'Agent rollback window %s (%s)' % (window['windowId'], window['agent'])

    def _api(self, method, path, body=None):
        request = urllib.request.Request('https://api.github.com/repos/%s%s' % (self.repo, path),
                                         method=method, data=json.dumps(body).encode() if body else None)
        request.add_header('Authorization', 'Bearer ' + self.token)
        request.add_header('Accept', 'application/vnd.github+json')
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode() or '{}')

    def mentions(self, escalate):
        people = list(self.window.get('onCall', []))
        if escalate:
            people += self.window.get('escalation', [])
        return ' '.join('@' + p.lstrip('@') for p in people)

    def send(self, headline, details, escalate=False, close=False):
        body = '**%s** — %s\n\n%s\n\n%s\n\n_Run: %s_' % (
            headline, iso(now()), details, self.mentions(escalate), ENV.get('ROLLBACK_RUN_URL', 'local'))
        body = redact(body)
        self.log.event('ALERT %s: %s' % (headline, details.replace('\n', ' | ')))
        if self.sink:
            with open(self.sink, 'a', encoding='utf-8') as handle:
                handle.write(json.dumps({'headline': headline, 'body': body, 'escalate': escalate}) + '\n')
            return True
        if not (self.repo and self.token):
            self.log.event('ALERT NOT SENT: no GitHub repository or token in this run')
            return False
        for attempt in range(3):
            try:
                if self.issue is None:
                    found = self._api('GET', '/issues?state=all&labels=agent-rollback&per_page=50')
                    match = [i for i in found if i.get('title') == self.title]
                    self.issue = match[0]['number'] if match else self._api(
                        'POST', '/issues', {'title': self.title, 'labels': ['agent-rollback'],
                                            'body': 'Rollback alerts for this window. Comment `/ack` to acknowledge.'})['number']
                self._api('POST', '/issues/%s/comments' % self.issue, {'body': body})
                if close:
                    self._api('PATCH', '/issues/%s' % self.issue, {'state': 'closed'})
                return True
            except Exception as failure:                       # alerting must never stop the rollback
                self.log.event('ALERT attempt %s failed: %s' % (attempt + 1, failure))
                time.sleep(5)
        return False

    def acknowledged(self):
        if self.sink or not (self.repo and self.token and self.issue):
            return False
        try:
            comments = self._api('GET', '/issues/%s/comments?per_page=100' % self.issue)
            on_call = {p.lstrip('@').lower() for p in self.window.get('onCall', []) + self.window.get('escalation', [])}
            return any(c.get('body', '').strip().lower().startswith('/ack') and
                       c.get('user', {}).get('login', '').lower() in on_call for c in comments)
        except Exception:
            return False


# ---------------------------------------------------------------- window file
def load_window(path):
    with open(path, encoding='utf-8') as handle:
        window = json.load(handle)
    for key in ('windowId', 'agent', 'safeVersion', 'armedAt', 'deadline', 'onCall'):
        if key not in window:
            raise ValueError('window file is missing %s' % key)
    armed = dt.datetime.fromisoformat(window['armedAt'].replace('Z', '+00:00'))
    deadline = dt.datetime.fromisoformat(window['deadline'].replace('Z', '+00:00'))
    latest = armed + dt.timedelta(minutes=MAX_WINDOW_MINUTES)
    window['_deadlineClamped'] = deadline > latest
    window['_deadline'] = min(deadline, latest)                 # C7: 90 minutes at most
    window.setdefault('grants', [])
    window.setdefault('loginAsOffAtDeadline', True)
    window.setdefault('escalation', [])
    return window


# ---------------------------------------------------------------- steps
class Rollback:
    def __init__(self, window, log, cli, alerts):
        self.w, self.log, self.cli, self.alerts = window, log, cli, alerts
        self.signed_in = False

    def sign_in(self):
        key = ENV.get('SF_JWT_KEY')
        missing = [n for n in ('SF_JWT_KEY', 'SF_CLIENT_ID', 'SF_USERNAME', 'SF_INSTANCE_URL') if not ENV.get(n)]
        if missing:
            return False, 'credentials not configured: %s' % ', '.join(missing)
        key_file = os.path.join(self.log.dir, '.jwt.key')
        old_mask = os.umask(0o077)
        try:
            with open(key_file, 'w') as handle:
                handle.write(key if key.endswith('\n') else key + '\n')
        finally:
            os.umask(old_mask)
        try:
            ok, _, message = self.cli.login(ENV['SF_USERNAME'], ENV['SF_INSTANCE_URL'], ENV['SF_CLIENT_ID'], key_file)
        finally:
            os.remove(key_file)                                 # the key never stays on disk or in the artefact
        self.signed_in = ok
        return ok, message

    def state_text(self, versions):
        return 'org %s · versions %s · grants still recorded: %s' % (
            ENV.get('SF_INSTANCE_URL', '?'), json.dumps(versions) if versions else 'unreadable',
            len(self.w['grants']))

    def confirmed(self, versions):
        if not versions:
            return False
        safe = int(self.w['safeVersion'])
        return versions.get(safe) == 'Active' and all(s != 'Active' for v, s in versions.items() if v != safe)

    def precheck(self):
        ok, message = self.sign_in()
        if not ok:
            self.alerts.send('R0 FAILED: rollback credential not valid', message, escalate=True)
            return False
        versions, error = self.cli.versions(self.w['agent'])
        if versions is None:
            self.alerts.send('R0 FAILED: cannot read agent versions', error, escalate=True)
            return False
        if int(self.w['safeVersion']) not in versions:
            self.alerts.send('R0 FAILED: safe version not found', self.state_text(versions), escalate=True)
            return False
        note = ' (deadline shortened to the 90-minute maximum)' if self.w['_deadlineClamped'] else ''
        self.alerts.send('Window armed', 'deadline %s%s\n%s' % (iso(self.w['_deadline']), note,
                                                            self.state_text(versions)))
        return True

    def wait_for_deadline(self):
        while now() < self.w['_deadline']:
            time.sleep(min(30, max(1, (self.w['_deadline'] - now()).total_seconds())))
        self.alerts.send('Deadline reached', 'rolling back to v%s now' % self.w['safeVersion'])

    def restore_version(self):
        """C3.1-3.3, 3.5: activate first, read back, retry with back-off, escalate after the hard limit."""
        start = now()
        attempt = 0
        last_escalation = None
        agent, safe = self.w['agent'], int(self.w['safeVersion'])
        while True:
            attempt += 1
            if not self.signed_in:
                ok, message = self.sign_in()
                if not ok:
                    self.alerts.send('Rollback attempt %s: sign-in failed' % attempt, message, escalate=attempt > 1)
            if self.signed_in:
                ok, _, message = self.cli.activate(agent, safe)          # never gated on a read
                self.log.event('attempt %s activate v%s -> %s %s' % (attempt, safe, 'ok' if ok else 'FAILED', message))
                if not ok and re.search(r'(?i)expired|invalid_grant|INVALID_SESSION|not authorized|No authorization',
                                        message):
                    self.signed_in = False                            # sign in again next attempt
                versions, error = self.cli.versions(agent)
                if self.confirmed(versions):
                    self.alerts.send('Rollback CONFIRMED', 'v%s Active, every other version Inactive (attempt %s)\n%s'
                                     % (safe, attempt, self.state_text(versions)))
                    return True
                self.alerts.send('Rollback NOT confirmed (attempt %s)' % attempt,
                                 '%s\nread-back error: %s\nnext retry in %ss' % (
                                     self.state_text(versions), error or 'none', BACKOFF[min(attempt - 1, len(BACKOFF) - 1)]),
                                 escalate=attempt > 1)
            elapsed = (now() - start).total_seconds()
            if elapsed >= HARD_LIMIT_SECONDS and (last_escalation is None or
                                                   (now() - last_escalation).total_seconds() >= ESCALATE_EVERY_SECONDS):
                if not self.alerts.acknowledged():
                    self.alerts.send('ESCALATION: rollback still not confirmed',
                                     'past the %s-minute limit. A person must take over now: Setup → Agents → %s → '
                                     'activate version %s.' % (HARD_LIMIT_SECONDS // 60, agent, safe), escalate=True)
                last_escalation = now()
            if elapsed >= GIVE_UP_SECONDS:
                self.alerts.send('Rollback job stopping without confirmation',
                                 'the job is about to time out. Roll back by hand now.', escalate=True)
                return False
            time.sleep(BACKOFF[min(attempt - 1, len(BACKOFF) - 1)])

    def remove_grants(self):
        """C3.4: remove each recorded grant and read it back. Only Ids listed in the window file are touched."""
        failures = []
        for grant in self.w['grants']:
            sobject, record_id = grant.get('sobject'), grant.get('id')
            if sobject not in ('PermissionSetAssignment', 'PermissionSetLicenseAssign') or \
                    not re.fullmatch(r'[A-Za-z0-9]{15,18}', record_id or ''):
                failures.append('refused unexpected grant entry %s' % json.dumps(grant))
                continue
            for attempt in range(3):
                self.cli.run(['data', 'delete', 'record', '--sobject', sobject, '--record-id', record_id,
                              '--target-org', ALIAS], 'remove-%s' % record_id)
                remaining, error = self.cli.query("SELECT Id FROM %s WHERE Id = '%s'" % (sobject, record_id),
                                                  'readback-%s' % record_id)
                if remaining == []:
                    self.log.event('grant %s %s removed (read back)' % (sobject, record_id))
                    break
                time.sleep(BACKOFF[0])
            else:
                failures.append('%s %s still present or unreadable: %s' % (sobject, record_id, error))
        return failures

    def login_as_off(self):
        """C3.4: deploy SecuritySettings.enableAdminLoginAsAnyUser=false, then retrieve and read it back."""
        folder = os.path.join(self.log.dir, 'loginas', 'force-app', 'main', 'default', 'settings')
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(self.log.dir, 'loginas', 'sfdx-project.json'), 'w') as handle:
            json.dump({'packageDirectories': [{'path': 'force-app', 'default': True}], 'sourceApiVersion': '68.0'}, handle)
        with open(os.path.join(folder, 'Security.settings-meta.xml'), 'w') as handle:
            handle.write('<?xml version="1.0" encoding="UTF-8"?>\n<SecuritySettings xmlns="http://soap.sforce.com/2006/04/metadata">\n'
                         '    <enableAdminLoginAsAnyUser>false</enableAdminLoginAsAnyUser>\n</SecuritySettings>\n')
        project = os.path.join(self.log.dir, 'loginas')
        for attempt in range(3):
            self.cli.run(['project', 'deploy', 'start', '--source-dir', 'force-app',
                          '--target-org', ALIAS, '--wait', '10'], 'loginas-off', cwd=project)
            ok, parsed, message = self.cli.run(['project', 'retrieve', 'start', '--metadata', 'Settings:Security',
                                                '--target-org', ALIAS, '--target-metadata-dir',
                                                'readback', '--unzip'], 'loginas-readback', cwd=project)
            text = ''
            for base, _, files in os.walk(os.path.join(project, 'readback')):
                for name in files:
                    if name.startswith('Security'):
                        text = open(os.path.join(base, name), encoding='utf-8').read()
            match = re.search(r'<enableAdminLoginAsAnyUser>(\w+)<', text)
            if match and match.group(1) == 'false':
                self.log.event('Log in as off (read back)')
                return None
            if not match and ok:                                # absent from the file means the default, off
                self.log.event('Log in as off (setting absent in read-back, default off)')
                return None
            time.sleep(BACKOFF[0])
        return 'Log in as could not be confirmed off: %s' % message

    def rollback(self):
        restored = self.restore_version()
        problems = self.remove_grants()
        if self.w['loginAsOffAtDeadline']:
            problem = self.login_as_off() if self.signed_in else 'not signed in: Log in as not changed'
            if problem:
                problems.append(problem)
        if problems:
            self.alerts.send('Access clean-up INCOMPLETE', '\n'.join(problems), escalate=True)
        else:
            self.alerts.send('Access clean-up confirmed', '%s grant(s) removed and read back; Log in as %s'
                             % (len(self.w['grants']), 'off' if self.w['loginAsOffAtDeadline'] else 'not changed'),
                             close=restored)
        return restored and not problems


def open_windows(log):
    """Armed windows whose deadline has not passed: window.json on every rollback-arm/* branch."""
    repo, token = ENV.get('GITHUB_REPOSITORY'), ENV.get('GITHUB_TOKEN')
    if ENV.get('ROLLBACK_OPEN_WINDOWS') is not None:          # tests
        return [w for w in ENV['ROLLBACK_OPEN_WINDOWS'].split(',') if w]
    if not (repo and token):
        return []
    found = []
    try:
        request = urllib.request.Request('https://api.github.com/repos/%s/git/matching-refs/heads/rollback-arm/' % repo)
        request.add_header('Authorization', 'Bearer ' + token)
        for ref in json.loads(urllib.request.urlopen(request, timeout=30).read().decode()):
            branch = ref['ref'][len('refs/heads/'):]
            raw = urllib.request.Request('https://api.github.com/repos/%s/contents/ops/agent-rollback/window.json?ref=%s'
                                         % (repo, branch))
            raw.add_header('Authorization', 'Bearer ' + token)
            raw.add_header('Accept', 'application/vnd.github.raw+json')
            path = os.path.join(LOG_DIR, 'w-%s.json' % re.sub(r'[^A-Za-z0-9]', '_', branch))
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(path, 'wb') as handle:
                handle.write(urllib.request.urlopen(raw, timeout=30).read())
            if load_window(path)['_deadline'] > now():
                found.append(branch)
    except Exception as failure:
        log.event('backstop: could not list armed windows (%s); enforcing the safe version anyway' % failure)
    return found


def backstop(window, log, cli, alerts):
    """Scheduled guard: outside an open window the safe version must be the Active one."""
    windows = open_windows(log)
    if windows:
        log.event('backstop: window still open on %s; its own job owns the rollback' % ', '.join(windows))
        return True
    rb = Rollback(window, log, cli, alerts)
    ok, message = rb.sign_in()
    if not ok:
        alerts.send('Backstop FAILED: rollback credential not valid', message, escalate=True)
        return False
    versions, error = cli.versions(window['agent'])
    if rb.confirmed(versions):
        log.event('backstop: safe version Active, nothing to do')
        return True
    alerts.send('Backstop: safe version not Active outside a window', rb.state_text(versions) + '\n' + (error or ''),
                escalate=True)
    return rb.restore_version()


def main(argv):
    if len(argv) < 3 or argv[1] not in ('precheck', 'window', 'rollback', 'backstop'):
        print(__doc__)
        return 2
    window = load_window(argv[2])
    log = Log(window['windowId'])
    cli = Cli(log)
    alerts = Alerts(log, window)
    log.event('mode %s · window %s · agent %s · safe v%s · deadline %s' % (
        argv[1], window['windowId'], window['agent'], window['safeVersion'], iso(window['_deadline'])))
    if argv[1] == 'backstop':
        return 0 if backstop(window, log, cli, alerts) else 1
    rb = Rollback(window, log, cli, alerts)
    if argv[1] == 'precheck':
        return 0 if rb.precheck() else 1
    if argv[1] == 'window':
        if not rb.precheck():
            # Fail towards rollback: a broken pre-check still leads to the rollback at the deadline.
            log.event('pre-check failed; continuing to the deadline so the rollback still runs')
        rb.wait_for_deadline()
    return 0 if rb.rollback() else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
