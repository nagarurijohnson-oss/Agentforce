"""S24 Phase B rollback watchdog. Runs detached (own session/process group, independent of the test harness).
usage: watchdog.py <deadline_minutes> [--dry-run]
Polls every 30 s. Exits quietly if s24/watchdog.stop exists. At the deadline: reads Contact_Read_Agent versions;
if v3 is not Active, runs `sf agent activate --api-name Contact_Read_Agent --version 3` and reads the versions back.
--dry-run: same flow, but only logs the command it would run (no activation). Only action ever taken: reactivate v3."""
import sys, os, json, time, subprocess
W = '/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'; O = 'orgfarm-232477b490-dev-ed'
E = {**os.environ, 'SF_DISABLE_LOG_FILE': 'true', 'SF_SKIP_NEW_VERSION_CHECK': 'true'}
LOG = W + '/s24/ev/watchdog.log'; STOP = W + '/s24/watchdog.stop'
mins = float(sys.argv[1]); dry = '--dry-run' in sys.argv
def log(m):
    open(LOG, 'a').write(time.strftime('%FT%TZ', time.gmtime()) + f' pid={os.getpid()} pgid={os.getpgid(0)} {"DRY " if dry else ""}{m}\n')
def versions():
    r = subprocess.run(['sf', 'data', 'query', '-o', O, '--json', '-q',
        "SELECT VersionNumber,Status FROM BotVersion WHERE BotDefinition.DeveloperName='Contact_Read_Agent'"],
        capture_output=True, text=True, timeout=180, env=E)
    return {x['VersionNumber']: x['Status'] for x in json.loads(r.stdout)['result']['records']}
deadline = time.time() + mins * 60
log(f'started; deadline {time.strftime("%FT%TZ", time.gmtime(deadline))} ({mins} min)')
while time.time() < deadline:
    if os.path.exists(STOP): log('stop file found; exiting without action'); sys.exit(0)
    time.sleep(min(30, max(1, deadline - time.time())))
if os.path.exists(STOP): log('stop file found at deadline; exiting without action'); sys.exit(0)
for attempt in range(3):
    try:
        v = versions()
        if dry and os.environ.get('WD_TEST_V7_ACTIVE') == '1': v = {**v, 3: 'Inactive', 7: 'Active'}  # dry-run test of the rollback branch only
        log(f'deadline reached; versions {v}')
        if v.get(3) == 'Active': log('v3 already Active; no action'); break
        cmd = ['sf', 'agent', 'activate', '--api-name', 'Contact_Read_Agent', '--version', '3', '--target-org', O, '--json']
        if dry: log('would run: ' + ' '.join(cmd)); break
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=E, cwd=W + '/Agentforce-kb')  # sf agent needs an SFDX project dir
        try: d = json.loads(r.stdout); log(f"activate v3 -> {d.get('status')} {str(d.get('message', ''))[:200]}")
        except Exception: log('activate v3 -> unparsed ' + (r.stdout + r.stderr)[-300:])
        v = versions(); log(f'read back {v}')
        if v.get(3) == 'Active':
            open(W + '/tasks/audit.log', 'a').write(time.strftime('%FT%TZ', time.gmtime()) + ' | 50144f18 | s24-watchdog | reactivated Contact_Read_Agent v3 at deadline\n')
            break
    except Exception as e: log(f'attempt {attempt + 1} failed: {str(e)[:200]}')
    time.sleep(60)
log('exiting')
