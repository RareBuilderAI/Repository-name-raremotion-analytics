import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
import analysis_access
import auth


class Client:
    def __init__(self):
        self.used = self.credits = self.calls = 0
        self.failure = False
        self.token = None
        self.auth = SimpleNamespace(get_session=lambda: SimpleNamespace(user=SimpleNamespace(id='test-user'), access_token='current-token'))
        self.postgrest = SimpleNamespace(auth=lambda token: setattr(self, 'token', token))

    def rpc(self, name):
        assert name == 'consume_analysis'
        self.calls += 1
        if self.failure:
            raise TimeoutError()
        allowed = self.used < 2 or self.credits > 0
        if self.used < 2:
            self.used += 1
        elif self.credits:
            self.credits -= 1
        return SimpleNamespace(execute=lambda: SimpleNamespace(data=[{'allowed': allowed}]))

    def table(self, name):
        return self

    def select(self, fields):
        return self

    def eq(self, key, value):
        return self

    def limit(self, count):
        return self

    def execute(self):
        assert self.token == 'current-token', 'Profile read must use the current user token'
        return SimpleNamespace(data=[{'free_analyses_used': self.used, 'paid_credits': self.credits}])


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.upload = io.BytesIO(b'Date,Product,Region,Category,Units,Revenue,Cost\n2026-01-01,A,West,Food,2,100,60\n')
        self.patches = [
            patch('auth.show_auth', return_value=SimpleNamespace(id='test-user')),
            patch('analysis_access.get_supabase', return_value=self.client),
            patch('streamlit.file_uploader', side_effect=lambda *a, **kw: self.file()),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'))

    def file(self):
        if self.upload:
            self.upload.seek(0)
        return self.upload

    def button(self, label):
        return next(b for b in self.app.button if b.label == label)

    def run_app(self):
        self.app.run(timeout=20)
        self.assertFalse(self.app.exception)

    def test_two_free_then_blocked_and_paid(self):
        self.run_app()
        self.assertEqual(self.client.calls, 0)
        self.assertEqual(len(self.app.header), 0)
        for expected in (1, 2):
            self.button('Analyze Data').click()
            self.run_app()
            self.assertEqual(self.client.used, expected)
            self.assertIn('Explore Your Data', [h.value for h in self.app.header])
            self.app.selectbox[1].select('Box Plot')
            self.run_app()
            self.assertEqual(self.client.calls, expected)
            self.button('Start another analysis').click()
            self.run_app()
        self.button('Analyze Data').click()
        self.run_app()
        self.assertEqual(self.client.used, 2)
        self.assertEqual(len(self.app.header), 0)
        self.assertIn('Payment required', self.app.error[0].value)
        self.client.credits = 1
        self.button('Start another analysis').click()
        self.run_app()
        self.button('Analyze Data').click()
        self.run_app()
        self.assertEqual(self.client.credits, 0)
        self.assertGreater(len(self.app.header), 0)

    def test_invalid_empty_missing_upload(self):
        for data in (None, b'', b'A,B\n', b'"unterminated'):
            self.upload = None if data is None else io.BytesIO(data)
            self.run_app()
            self.assertEqual(self.client.calls, 0)
            self.assertFalse(self.app.button)

    def test_changed_file_requires_new_action(self):
        self.run_app()
        self.button('Analyze Data').click()
        self.run_app()
        self.upload = io.BytesIO(b'Revenue,Cost\n200,50\n')
        self.run_app()
        self.assertEqual(len(self.app.header), 0)
        self.assertEqual(self.client.calls, 1)

    def test_timeout_does_not_retry(self):
        self.client.failure = True
        self.run_app()
        self.button('Analyze Data').click()
        self.run_app()
        self.run_app()
        self.assertEqual(self.client.calls, 1)
        self.assertEqual(len(self.app.header), 0)
        self.assertTrue(self.button('Analyze Data').disabled)

    def test_client_is_kept_per_session(self):
        class State(dict):
            __getattr__ = dict.__getitem__
            __setattr__ = dict.__setitem__
        with patch.object(auth.st, 'session_state', State()), patch.object(auth.st, 'secrets', {'SUPABASE_URL': 'test', 'SUPABASE_KEY': 'test'}), patch.object(auth, 'create_client', return_value=self.client) as factory:
            self.assertIs(auth.get_supabase(), auth.get_supabase())
            factory.assert_called_once()
        with patch.object(auth.st, 'session_state', State()), patch.object(auth.st, 'secrets', {'SUPABASE_URL': 'test', 'SUPABASE_KEY': 'test'}), patch.object(auth, 'create_client') as factory:
            auth.get_supabase()
            factory.assert_called_once()

    def test_malformed_responses_fail_closed(self):
        for data in (None, [], {}, {'allowed': 'true'}, [{'allowed': True}, {'allowed': True}]):
            client = SimpleNamespace(rpc=lambda name: SimpleNamespace(execute=lambda: SimpleNamespace(data=data)))
            with self.assertRaises(ValueError):
                analysis_access.consume_analysis(client)

    def test_usage_read_binds_current_session_and_accepts_zero(self):
        self.assertEqual(analysis_access.read_usage(self.client, 'test-user'), (0, 0))
        self.assertEqual(self.client.token, 'current-token')
        self.assertEqual(self.client.calls, 0)

    def test_usage_read_rejects_other_user_and_missing_session(self):
        with self.assertRaises(auth.SessionUnavailable):
            analysis_access.read_usage(self.client, 'another-user')
        self.client.auth.get_session = lambda: None
        with self.assertRaises(auth.SessionUnavailable):
            analysis_access.read_usage(self.client, 'test-user')
        self.assertIsNone(self.client.token)

    def test_usage_read_missing_profile_is_not_zero_allowance(self):
        self.client.execute = lambda: SimpleNamespace(data=[])
        with self.assertRaises(LookupError):
            analysis_access.read_usage(self.client, 'test-user')

    def test_token_refresh_rebinds_database_client(self):
        auth.bind_authenticated_session(self.client, 'test-user')
        self.client.auth.get_session = lambda: SimpleNamespace(user=SimpleNamespace(id='test-user'), access_token='refreshed-token')
        auth.bind_authenticated_session(self.client, 'test-user')
        self.assertEqual(self.client.token, 'refreshed-token')


if __name__ == '__main__':
    unittest.main()
