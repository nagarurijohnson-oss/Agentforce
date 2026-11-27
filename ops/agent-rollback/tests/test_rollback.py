"""Mock tests for ops/agent-rollback/rollback.py (OPS-1 C6 T1, T3, T4, T5, T6 without an org).
Run: python3 -m unittest discover -s ops/agent-rollback/tests -v"""
import datetime as dt, json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, '..', 'rollback.py')
FAKE_SF = os.path.join(HERE, 'fake_bin', 'sf')
FAKE_KEY = '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCfakefakefake\n-----END PRIVATE KEY-----'

class RollbackMock(unittest.TestCase):
    def run_case(self, state, mode='rollback', grants=None, creds=True, extra_env=None):
        tmp = tempfile.mkdtemp()
        now = dt.datetime.now(dt.timezone.utc)
        window = {'windowId': 'mock', 'agent': 'Contact_Read_Agent', 'safeVersion': 3,
                  'armedAt': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'deadline': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
                  'onCall': ['oncall-person'], 'escalation': ['escalation-person'], 'grants': grants or [],
                  'loginAsOffAtDeadline': True}
        json.dump(window, open(os.path.join(tmp, 'window.json'), 'w'))
        json.dump(state, open(os.path.join(tmp, 'state.json'), 'w'))
        env = {'PATH': os.environ['PATH'], 'FAKE_SF_STATE': os.path.join(tmp, 'state.json'),
               'ROLLBACK_SF': FAKE_SF, 'ROLLBACK_LOG_DIR': os.path.join(tmp, 'logs'),
               'ROLLBACK_ALERT_SINK': os.path.join(tmp, 'alerts.jsonl'), 'ROLLBACK_BACKOFF': '0',
               'ROLLBACK_HARD_LIMIT_SECONDS': '0', 'ROLLBACK_ESCALATE_EVERY_SECONDS': '0',
               'ROLLBACK_GIVE_UP_SECONDS': '2'}
        if creds:
            env.update({'SF_JWT_KEY': FAKE_KEY, 'SF_CLIENT_ID': '3MVG9FakeClientIdValue0123456789',
                        'SF_USERNAME': 'rollback@example', 'SF_INSTANCE_URL': 'https://example.my.salesforce.com'})
        env.update(extra_env or {})
        proc = subprocess.run([sys.executable, SCRIPT, mode, os.path.join(tmp, 'window.json')],
                              capture_output=True, text=True, env=env, timeout=120)
        alerts = [json.loads(l) for l in open(env['ROLLBACK_ALERT_SINK'])] if os.path.exists(env['ROLLBACK_ALERT_SINK']) else []
        logdir = os.path.join(tmp, 'logs', 'mock')
        saved = ''
        for base, _, files in os.walk(os.path.join(tmp, 'logs')):
            for f in files:
                saved += open(os.path.join(base, f), encoding='utf-8', errors='replace').read()
        return proc, json.load(open(env['FAKE_SF_STATE'])), alerts, saved, logdir

    def headlines(self, alerts):
        return [a['headline'] for a in alerts]

    def test_t1_normal_deadline(self):
        proc, state, alerts, saved, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(state['versions'], {'3': 'Active', '7': 'Inactive'})
        self.assertIn('Rollback CONFIRMED', self.headlines(alerts))
        self.assertIn('Access clean-up confirmed', self.headlines(alerts))

    def test_t1_noop_when_safe_already_active(self):
        proc, state, alerts, _, _ = self.run_case({'versions': {'3': 'Active', '7': 'Inactive'}})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(state['versions']['3'], 'Active')

    def test_t3_expired_credentials_fail_loudly_and_keep_retrying(self):
        proc, state, alerts, saved, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}, 'login': 'expired'})
        self.assertNotEqual(proc.returncode, 0, 'a rollback that cannot be confirmed must fail the job')
        attempts = [h for h in self.headlines(alerts) if 'sign-in failed' in h]
        self.assertGreaterEqual(len(attempts), 2, 'retries continue after a failed sign-in')
        self.assertTrue(any('invalid_grant' in a['body'] for a in alerts), 'the CLI error is in the alert')
        self.assertIn('invalid_grant', saved, 'the full CLI error is saved')
        self.assertTrue(any(a['escalate'] for a in alerts), 'escalation contact is named')
        self.assertIn('Rollback job stopping without confirmation', self.headlines(alerts))
        self.assertEqual(state['versions']['7'], 'Active', 'nothing claims success')

    def test_t3b_credentials_missing(self):
        proc, _, alerts, _, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}}, creds=False)
        self.assertNotEqual(proc.returncode, 0)
        self.assertTrue(any('credentials not configured' in a['body'] for a in alerts))

    def test_t3c_recovers_when_credential_starts_working(self):
        proc, state, alerts, _, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}, 'loginFailures': 2})
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertEqual(state['versions']['3'], 'Active')

    def test_t4_readback_error_still_activates_and_retries(self):
        proc, state, alerts, saved, _ = self.run_case(
            {'versions': {'3': 'Inactive', '7': 'Active'}, 'queryFailures': 2, 'activateFailures': 1})
        self.assertEqual(proc.returncode, 0, proc.stdout)
        log = state['log']
        self.assertTrue(log.index('agent activate --api-name') < log.index('data query --target-org'),
                        'activate is attempted before any read')
        self.assertGreaterEqual(log.count('agent activate --api-name'), 2, 'activate retried')
        self.assertIn('INVALID_SESSION_ID', saved, 'read-back error saved')
        self.assertIn('Rollback CONFIRMED', self.headlines(alerts))

    def test_t5_grants_removed_and_login_as_off(self):
        grants = [{'sobject': 'PermissionSetAssignment', 'id': '0PajV00000AAAAAAAA'},
                  {'sobject': 'PermissionSetLicenseAssign', 'id': '2LAjV00000BBBBBBBB'},
                  {'sobject': 'User', 'id': '005jV000003sYUPQA2'}]
        proc, state, alerts, saved, _ = self.run_case(
            {'versions': {'3': 'Active', '7': 'Inactive'}, 'grants': ['0PajV00000AAAAAAAA', '2LAjV00000BBBBBBBB',
                                                                     '005jV000003sYUPQA2'], 'loginAs': True},
            grants=grants)
        self.assertEqual(state['grants'], ['005jV000003sYUPQA2'], 'only listed grant records are deleted')
        self.assertFalse(state['loginAs'])
        self.assertNotEqual(proc.returncode, 0, 'the refused entry is reported')
        self.assertTrue(any('refused unexpected grant entry' in a['body'] for a in alerts))

    def test_t6_logging_hygiene(self):
        proc, _, alerts, saved, logdir = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}, 'leak': True})
        everything = saved + proc.stdout + proc.stderr + json.dumps(alerts)
        for secret in ('FakeTokenValue', 'AnotherFake', 'SecretFromLogin', 'MIIEvQIBADANBgkqhkiG9w0', '3MVG9FakeClientIdValue'):
            self.assertNotIn(secret, everything, secret + ' leaked')
        self.assertIn('[REDACTED', saved)
        self.assertFalse(any(f.endswith('.key') for f in os.listdir(logdir)), 'no key file left behind')
        self.assertTrue(os.path.exists(os.path.join(logdir, 'calls.jsonl')))
        first = json.loads(open(os.path.join(logdir, 'calls.jsonl')).readline())
        for key in ('ts', 'end', 'argv', 'exit', 'stdout', 'stderr'):
            self.assertIn(key, first)

    def test_backstop_skips_open_window_and_enforces_otherwise(self):
        proc, state, _, _, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}}, mode='backstop',
                                             extra_env={'ROLLBACK_OPEN_WINDOWS': 'rollback-arm/x'})
        self.assertEqual(state['versions']['7'], 'Active', 'an open window is left to its own job')
        proc, state, _, _, _ = self.run_case({'versions': {'3': 'Inactive', '7': 'Active'}}, mode='backstop',
                                             extra_env={'ROLLBACK_OPEN_WINDOWS': ''})
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(state['versions']['3'], 'Active')

    def test_window_longer_than_90_minutes_is_clamped(self):
        sys.path.insert(0, os.path.join(HERE, '..'))
        import rollback
        tmp = tempfile.mkdtemp(); p = os.path.join(tmp, 'w.json')
        json.dump({'windowId': 'x', 'agent': 'A', 'safeVersion': 3, 'armedAt': '2026-12-01T09:00:00Z',
                   'deadline': '2026-12-01T20:00:00Z', 'onCall': []}, open(p, 'w'))
        w = rollback.load_window(p)
        self.assertTrue(w['_deadlineClamped'])
        self.assertEqual(rollback.iso(w['_deadline']), '2026-12-01T10:30:00Z')

if __name__ == '__main__':
    unittest.main()
