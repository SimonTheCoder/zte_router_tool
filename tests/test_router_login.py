import hashlib
import os
import unittest
from unittest.mock import MagicMock, patch
from src.router import ZTERouter

class TestZTERouterLogin(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://192.168.1.1"
        self.username = "admin"
        self.password = os.getenv("ROUTER_PWD", "test_password")
        self.router = ZTERouter(self.base_url, self.username, self.password)

    @patch('requests.Session.get')
    @patch('requests.Session.post')
    def test_login_success(self, mock_post, mock_get):
        # Mocking Step A: Get login tokens
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "_sessionToken": "test_stoken_123",
            "logintoken": "29778210"
        }
        mock_get.return_value = mock_get_response

        # Mocking Step B: Authentication
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "sess_token": "final_sess_token_456",
            "login_need_refresh": True,
            "loginErrType": ""
        }
        mock_post.return_value = mock_post_response

        # Execute login
        result = self.router.login()

        # Assertions
        self.assertTrue(result)
        self.assertEqual(self.router.session_token, "final_sess_token_456")
        
        # Verify Step A call
        mock_get.assert_called_once_with(
            f"{self.base_url}/?_type=loginsceneData&_tag=login_token_json",
            headers={"Referer": f"{self.base_url}/"}
        )
        
        # Verify Step B call
        # Verify the password was hashed with the login token (SHA-256 of password+logintoken)
        mock_login_token = "29778210"
        expected_password_hash = hashlib.sha256((self.password + mock_login_token).encode()).hexdigest()
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"{self.base_url}/?_type=loginData&_tag=login_entry")
        self.assertEqual(kwargs['data']['Password'], expected_password_hash)
        self.assertEqual(kwargs['data']['_sessionTOKEN'], "test_stoken_123")

    @patch('requests.Session.get')
    def test_login_token_failure(self, mock_get):
        # Mocking Step A failure
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {} # Missing tokens
        mock_get.return_value = mock_get_response

        with self.assertRaises(ValueError) as cm:
            self.router.login()
        self.assertEqual(str(cm.exception), "Failed to acquire login tokens")

if __name__ == '__main__':
    unittest.main()
