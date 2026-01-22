# 🎧 Tracker Bot Listener 

**Host:** Vercel (Serverless Function)
**Role:** Handles incoming Discord Slash Commands via Webhooks.

> **Note:** This repository is **Part 2** of the Universal Discord Tracker system.
> * **Part 1 (The Watcher):** [Link to Part 1](https://github.com/ppanturat/tracker-bot)
> * **Part 2 (The Listener):** You are here.

---

## ⚡ How it Works
This component is the **Serverless API** that connects Discord to your Database.

1.  User types `/track` or `/add_stock` in Discord.
2.  Discord sends an HTTP POST request to Vercel (`/api/interactions`).
3.  **`api/index.py`** processes the request (connects to Supabase, calls APIs).
4.  Vercel sends a JSON response back to Discord instantly.

---

## 🛠️ Deployment Guide

### 1. Environment Variables (Vercel)
To deploy this yourself, you must set these variables in your **Vercel Project Settings**:

| Key | Purpose | Source |
| :--- | :--- | :--- |
| `DISCORD_PUBLIC_KEY` | Security verification. | Discord Developer Portal |
| `SUPABASE_URL` | Database connection. | Supabase Dashboard |
| `SUPABASE_KEY` | Database access. | Supabase Dashboard |
| `TRACK17_KEY` | Parcel tracking API. | 17Track Developer Center |

### 2. Local Setup (for development)
If you want to modify the code or register new commands locally:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/tracker-listener.git](https://github.com/your-username/tracker-listener.git)
    cd tracker-listener
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Local Secrets:**
    Create a file named `.env` in the root folder and add your keys (this file is ignored by Git):
    ```ini
    APP_ID=your_app_id_here
    BOT_TOKEN=your_bot_token_here
    ```

---

## 💻 How to Add New Commands

### Phase 1: The Logic (Vercel)
The backend logic lives in **`api/index.py`**.

1.  Find the `interactions()` function.
2.  Add a new block for your command:
    ```python
    elif command_name == "my_new_command":
        # Your logic here
        return jsonify({...})
    ```
3.  **Push to GitHub.** Vercel will auto-deploy the changes.

### Phase 2: The Interface (Discord)
You must explicitly tell Discord that this new command exists.

1.  Open **`register_commands.py`** locally.
2.  Add your command definition to the `json_commands` list.
3.  Run the script (it loads credentials from your `.env` file):
    ```bash
    python register_commands.py
    ```
4.  If you see `200` or `201`, the command is live.

---

## 📂 File Structure

* **`api/index.py`**
    * The main entry point for Vercel.
    * **Do not rename this file.** Vercel looks specifically for this path.
    * Contains the logic for `/add_stock`, `/track`, `/parcels`, etc.

* **`register_commands.py`**
    * Local utility script. **Does NOT run on Vercel.**
    * Used to update the Discord "Slash Command" menu.
    * *Secure:* Loads `APP_ID` and `BOT_TOKEN` from `.env` to prevent leaks.

* **`requirements.txt`**
    * List of Python libraries (`flask`, `requests`, `supabase`, `discord-interactions`, `python-dotenv`).

* **`vercel.json`**
    * Configuration file telling Vercel how to build the Python runtime.

---

## 🐛 Troubleshooting

**Issue: "Interaction Failed"**
* **Check:** Vercel Logs (Dashboard -> Deployments -> [Latest] -> Logs).
* **Common Cause:** Code took >3 seconds. Discord times out requests after 3 seconds.
* **Fix:** Optimize SQL queries or API calls.

**Issue: Command not showing up in Discord**
* Did you run `register_commands.py` locally?
* Did the script output `200`? If `400`, check your JSON syntax.

**Issue: `ModuleNotFoundError: No module named 'dotenv'`**
* You likely forgot to install the new dependency. Run `pip install python-dotenv`.

---
*Created for Personal Use.*
