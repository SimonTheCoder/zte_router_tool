import subprocess
import time
import logging
import platform

logger = logging.getLogger(__name__)

def ping(host):
    """
    Returns True if host responds to a ping request.
    """
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

class NetworkMonitor:
    def __init__(self, target, gateway, interval=60, max_failures=3):
        self.target = target
        self.gateway = gateway
        self.interval = interval
        self.max_failures = max_failures
        self.failure_count = 0

    def check_connectivity(self):
        if ping(self.target):
            if self.failure_count > 0:
                logger.info(f"Connectivity restored to {self.target}")
            self.failure_count = 0
            return True
        else:
            self.failure_count += 1
            logger.warning(f"Ping failed to {self.target} ({self.failure_count}/{self.max_failures})")
            return False

    def is_down(self):
        return self.failure_count >= self.max_failures

    def check_gateway(self):
        return ping(self.gateway)
