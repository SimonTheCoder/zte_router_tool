# ZTE Router Network Monitor & Automated Redialer

This tool monitors your internet connectivity by pinging a target (default: 8.8.8.8). If the connection fails multiple times but the router is still reachable, it automatically logs into the ZTE router and triggers a PPPoE redial.

## Features
- Connectivity monitoring via ICMP ping.
- Automatic login using SHA256 hashed passwords (salted with `logintoken`).
- Automated PPPoE redial (`PPPONRECONNECT`).
- Detailed logging to `router_monitor.log`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (Or use `pip install requests python-dotenv`)

2. Configure `.env` file:
   - `ROUTER_URL`: The IP address of your router (e.g., `http://192.168.1.1`).
   - `ROUTER_USER`: Your router login username.
   - `ROUTER_PWD`: Your router login password.
   - `CHECK_INTERVAL`: How often to check connectivity (in seconds).
   - `PING_TARGET`: The IP to ping to check for internet.
   - `MAX_FAILURES`: Number of consecutive ping failures before triggering a redial.

## Usage

Run the monitor script:
```bash
python main.py
```

## Security Note
The `.env` file contains your router password in plaintext. Ensure this file is kept secure and not shared.
