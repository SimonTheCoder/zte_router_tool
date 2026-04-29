import requests
import hashlib
import logging
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class ZTERouter:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_token = None

    def _get_login_tokens(self):
        """Step A: Token Acquisition (GET)"""
        url = f"{self.base_url}/?_type=loginsceneData&_tag=login_token_json"
        headers = {
            "Referer": f"{self.base_url}/"
        }
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("_sessionToken"), data.get("logintoken")

    def login(self):
        """Step B: Authentication (POST)"""
        stoken, ltoken = self._get_login_tokens()
        if not stoken or not ltoken:
            raise ValueError("Failed to acquire login tokens")

        password_hash = hashlib.sha256((self.password + ltoken).encode()).hexdigest()
        
        url = f"{self.base_url}/?_type=loginData&_tag=login_entry"
        headers = {
            "Referer": f"{self.base_url}/",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "Username": self.username,
            "Password": password_hash,
            "action": "login",
            "Frm_Logintoken": "",
            "captchaCode": "",
            "_sessionTOKEN": stoken
        }
        
        response = self.session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("sess_token"):
            # Use X_XSRF_TOKEN from response headers if available (server-provided session token)
            # otherwise fall back to sess_token from response body
            self.session_token = response.headers.get("X_XSRF_TOKEN") or data.get("sess_token")
            logger.info("Login successful")
            return True
        else:
            logger.error(f"Login failed: {data}")
            return False

    def _refresh_token(self):
        """Fetch a fresh XSRF token by GETting the target page (mirrors browser behavior)."""
        url = f"{self.base_url}/?_type=vueData&_tag=home_internetreg_lua"
        headers = {"Referer": f"{self.base_url}/"}
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        new_token = response.headers.get("X_XSRF_TOKEN")
        if new_token:
            self.session_token = new_token
            logger.debug(f"Token refreshed: {new_token}")
        return new_token is not None

    def redial(self):
        """Step C: Reconnect Command (POST)"""
        if not self.session_token:
            if not self.login():
                return False

        # Refresh token before redial — the login token is stale for page actions
        if not self._refresh_token():
            logger.error("Failed to refresh session token before redial")
            return False

        url = f"{self.base_url}/?_type=vueData&_tag=home_internetreg_lua"
        headers = {
            "Referer": f"{self.base_url}/",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "IF_ACTION": "PPPONRECONNECT",
            "WAN_INST": "wan1",
            "_sessionTOKEN": self.session_token
        }
        
        response = self.session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        
        # Update session token from X_XSRF_TOKEN header for subsequent requests
        xsrf_token = response.headers.get("X_XSRF_TOKEN")
        if xsrf_token:
            self.session_token = xsrf_token
        
        # The response is XML
        try:
            root = ET.fromstring(response.text)
            error_str = root.find("IF_ERRORSTR").text
            if error_str == "SUCC":
                logger.info("Redial command sent successfully")
                return True
            else:
                logger.error(f"Redial failed: {error_str}")
                return False
        except Exception as e:
            logger.error(f"Failed to parse redial response: {e}")
            return False
