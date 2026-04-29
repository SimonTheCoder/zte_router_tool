## **Project: Router Network Monitor & Automated PPPoE Redialer**

### **1. Objective**
Create a Python script that monitors internet connectivity. [cite_start]If the connection fails while the router is still reachable, the script will automate a login and trigger a `PPPONRECONNECT` action[cite: 80].

### **2. Phase 0: Hashing Discovery (The "Chrome DevTools" Phase)**
[cite_start]Before coding, you must identify how the plaintext password becomes the 64-character hash (e.g., `032d86...`) seen in the logs[cite: 46].

* **Step 1 (Source Inspection):** Open `http://192.168.1.1` in Chrome. Open **DevTools (F12)** -> **Sources** tab.
* **Step 2 (Search):** Search (Ctrl+Shift+F) for keywords: `login_entry`, `Password`, `hex_sha256`, or `encrypt`.
* **Step 3 (Breakpoint Analysis):** Locate the JavaScript function handling the login form submission. Set a breakpoint on the line where the password variable is processed.
* **Step 4 (Variable Inspection):** Trigger a login attempt. When the breakpoint hits, check the console for:
    * Is the hash a simple `SHA256(password)`?
    * [cite_start]Is it salted, such as `SHA256(password + logintoken)`?[cite: 27, 47].
    * [cite_start]Does it use the `_sessionToken` as a pepper?[cite: 27, 81].

### **3. Phase 1: Connectivity Monitor**
* **Health Check:** Ping `8.8.8.8` every 60 seconds.
* [cite_start]**Failure Logic:** On 3 consecutive failures, check if the gateway `192.168.1.1` responds[cite: 29, 63]. If the gateway is alive, initiate the **Redial Procedure**.

### **4. Phase 2: Redial Procedure (Automated Sequence)**

#### **Step A: Token Acquisition (GET)**
* [cite_start]**Target:** `http://192.168.1.1/?_type=loginsceneData&_tag=login_token_json`[cite: 3].
* [cite_start]**Extraction:** Parse JSON to retrieve `_sessionToken` and `logintoken`[cite: 27].
* [cite_start]**Session:** Maintain a `requests.Session()` to store the `SID` cookie[cite: 20, 26].

#### **Step B: Authentication (POST)**
* [cite_start]**Target:** `http://192.168.1.1/?_type=loginData&_tag=login_entry`[cite: 32].
* [cite_start]**Headers:** `Referer: http://192.168.1.1/`[cite: 38].
* **Payload (URL-Encoded):**
    * [cite_start]`Username`: `admin`[cite: 46].
    * [cite_start]`Password`: The hash derived from the logic found in **Phase 0**[cite: 46].
    * [cite_start]`_sessionTOKEN`: The token from Step A[cite: 48].
    * [cite_start]`action`: `login`[cite: 46].

#### **Step C: Reconnect Command (POST)**
* [cite_start]**Target:** `http://192.168.1.1/?_type=vueData&_tag=home_internetreg_lua`[cite: 66].
* **Payload:**
    * [cite_start]`IF_ACTION`: `PPPONRECONNECT`[cite: 80].
    * [cite_start]`WAN_INST`: `wan1`[cite: 80].
    * [cite_start]`_sessionTOKEN`: The latest valid session token[cite: 81].
* [cite_start]**Validation:** Confirm the XML response contains `<IF_ERRORSTR>SUCC</IF_ERRORSTR>`[cite: 93].

### **5. Environment & Safety**
* **Credentials:** Do not hardcode. Use a `.env` file for `ROUTER_USER` and `ROUTER_PWD`.
* **Logging:** Record all pings and redial attempts in `router_monitor.log`.
* [cite_start]**Cool-down:** After a redial, pause the monitor for 60 seconds to allow the PPPoE session to stabilize[cite: 93].
