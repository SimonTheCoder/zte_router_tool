import os
import logging
from dotenv import load_dotenv
from src.router import ZTERouter

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_login():
    load_dotenv()
    
    router_url = os.getenv("ROUTER_URL", "http://192.168.1.1")
    username = os.getenv("ROUTER_USER", "admin")
    password = os.getenv("ROUTER_PWD")
    
    if not password:
        logger.error("ROUTER_PWD not set in .env file")
        return

    logger.info(f"Attempting real login to {router_url} as {username}...")
    router = ZTERouter(router_url, username, password)
    
    try:
        success = router.login()
        if success:
            logger.info("✅ SUCCESS: Login successful!")
            logger.info(f"Session Token: {router.session_token}")
        else:
            logger.error("❌ FAILURE: Login failed. Check your credentials or router state.")
    except Exception as e:
        logger.error(f"❌ ERROR: An exception occurred during login: {e}")

if __name__ == "__main__":
    test_real_login()
