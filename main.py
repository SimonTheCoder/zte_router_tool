import os
import time
import logging
import argparse
from dotenv import load_dotenv
from src.router import ZTERouter
from src.monitor import NetworkMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("router_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_once(monitor, router, force=False):
    """Performs a single connectivity check and attempts redial if necessary."""
    if force:
        logger.info("Force mode: skipping ping test, redialing immediately...")
        if router.redial():
            logger.info("Redial successful.")
            return True
        else:
            logger.error("Redial failed.")
            return False

    logger.info("Performing single connectivity check...")
    if monitor.check_connectivity():
        logger.info("Network is up. No action needed.")
        return True

    logger.warning("Network is down. Checking gateway...")
    if monitor.check_gateway():
        logger.info("Gateway is reachable. Attempting redial...")
        if router.redial():
            logger.info("Redial successful.")
            return True
        else:
            logger.error("Redial failed.")
            return False
    else:
        logger.error("Gateway is unreachable. Please check the router connection.")
        return False

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="ZTE Router Network Monitor & Automated Redialer")
    parser.add_argument("--oneshot", "-o", action="store_true", help="Perform a single check/redial and exit")
    parser.add_argument("--force", "-f", action="store_true", help="Skip ping test and redial immediately")
    args = parser.parse_args()
    
    router_url = os.getenv("ROUTER_URL", "http://192.168.1.1")
    username = os.getenv("ROUTER_USER", "admin")
    password = os.getenv("ROUTER_PWD")
    check_interval = int(os.getenv("CHECK_INTERVAL", "60"))
    ping_target = os.getenv("PING_TARGET", "8.8.8.8")
    max_failures = int(os.getenv("MAX_FAILURES", "3"))
    
    if not password:
        logger.error("ROUTER_PWD not set in .env file")
        return

    # Extract gateway IP from router_url
    gateway = router_url.split("//")[-1].split(":")[0].split("/")[0]
    
    router = ZTERouter(router_url, username, password)
    monitor = NetworkMonitor(ping_target, gateway, check_interval, max_failures)
    
    if args.oneshot:
        run_once(monitor, router, force=args.force)
        return

    logger.info("Starting router network monitor loop...")
    
    while True:
        try:
            if args.force:
                logger.info("Force mode: skipping ping test, redialing immediately...")
                if router.redial():
                    logger.info("Redial successful. Waiting 60s for stabilization...")
                    time.sleep(60)
                else:
                    logger.error("Redial failed.")
            elif not monitor.check_connectivity():
                if monitor.is_down():
                    logger.warning("Network is down. Checking gateway...")
                    if monitor.check_gateway():
                        logger.info("Gateway is reachable. Attempting redial...")
                        if router.redial():
                            logger.info("Redial successful. Waiting 60s for stabilization...")
                            time.sleep(60)
                        else:
                            logger.error("Redial failed.")
                    else:
                        logger.error("Gateway is unreachable. Please check the router connection.")

            time.sleep(monitor.interval)
        except KeyboardInterrupt:
            logger.info("Monitor stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(monitor.interval)

if __name__ == "__main__":
    main()
