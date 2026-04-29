import os
import unittest
from unittest.mock import MagicMock, patch
from src.router import ZTERouter

class TestZTERouterRedial(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://192.168.1.1"
        self.username = "admin"
        self.password = os.getenv("ROUTER_PWD", "test_password")
        self.router = ZTERouter(self.base_url, self.username, self.password)
        self.router.session_token = "existing_sess_token"

    @patch('requests.Session.post')
    def test_redial_success(self, mock_post):
        # Mocking Step C: Reconnect Command
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = "<ajax_response_xml_root><IF_ERRORSTR>SUCC</IF_ERRORSTR></ajax_response_xml_root>"
        mock_post_response.headers = {"X_XSRF_TOKEN": "new_xsrf_token"}
        mock_post.return_value = mock_post_response

        # Execute redial
        result = self.router.redial()

        # Assertions
        self.assertTrue(result)
        self.assertEqual(self.router.session_token, "new_xsrf_token")
        
        # Verify POST call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], f"{self.base_url}/?_type=vueData&_tag=home_internetreg_lua")
        self.assertEqual(kwargs['data']['IF_ACTION'], "PPPONRECONNECT")
        self.assertEqual(kwargs['data']['_sessionTOKEN'], "existing_sess_token")

    @patch('requests.Session.post')
    def test_redial_failure_xml(self, mock_post):
        # Mocking Step C failure in XML
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.text = "<ajax_response_xml_root><IF_ERRORSTR>FAIL</IF_ERRORSTR></ajax_response_xml_root>"
        mock_post.return_value = mock_post_response

        # Execute redial
        result = self.router.redial()

        # Assertions
        self.assertFalse(result)

    @patch('requests.Session.post')
    def test_redial_auto_login(self, mock_post):
        # Test that redial calls login if session_token is missing
        self.router.session_token = None
        
        with patch.object(self.router, 'login') as mock_login:
            mock_login.return_value = True
            # We need to manually set session_token because mock_login won't do it
            def side_effect():
                self.router.session_token = "token_after_login"
                return True
            mock_login.side_effect = side_effect

            mock_post_response = MagicMock()
            mock_post_response.status_code = 200
            mock_post_response.text = "<ajax_response_xml_root><IF_ERRORSTR>SUCC</IF_ERRORSTR></ajax_response_xml_root>"
            mock_post.return_value = mock_post_response

            # Execute redial
            result = self.router.redial()

            # Assertions
            self.assertTrue(result)
            mock_login.assert_called_once()
            self.assertEqual(kwargs_post['data']['_sessionTOKEN'], "token_after_login") if 'kwargs_post' in locals() else None
            
            # Verify POST call used the new token
            args, kwargs = mock_post.call_args
            self.assertEqual(kwargs['data']['_sessionTOKEN'], "token_after_login")

if __name__ == '__main__':
    unittest.main()
