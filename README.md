# 🤖 PC-Control Telegram Bot

Control your PC remotely from **anywhere in the world** using Telegram. Powered by **Google Gemini AI**, this bot lets you control your computer using natural language — no need to remember commands.

---

## ✨ Features

### 🧠 Natural Language Control (Gemini AI)
Just chat with the bot in plain English. Gemini interprets your intent and maps it to the right command automatically.
- _"Turn off the computer in 2 hours"_ → runs `/shutdown_h 2`
- _"Show me the desktop"_ → runs `/minimize`
- _"What's my CPU usage?"_ → runs `/sysinfo`

### 🖥️ Remote Control
| Feature | Description |
| --- | --- |
| **Shutdown / Reboot** | Schedule or immediate shutdown and reboot |
| **Program Launcher** | Launch any installed program by name |
| **Process Killer** | Fuzzy-match and kill running processes (including children) |
| **Web Navigation** | Open any URL in the default browser |
| **Type Text** | Type text remotely (ASCII direct-type + Unicode clipboard-paste mode) |
| **Volume Control** | Set system volume 0–100% |
| **Brightness Control** | Set screen brightness 0–100% |
| **Lock Screen** | Lock the PC instantly |
| **Close Window** | Close the currently active window |
| **Minimize All** | Show the desktop (Win+D) |
| **Clipboard** | Read the current clipboard text |
| **Empty Trash** | Empty the Recycle Bin |
| **Cancel** | Cancel a pending shutdown/reboot timer |

### 📸 Media & Visuals
| Feature | Description |
| --- | --- |
| **Screenshot (Monitor 1)** | Capture and send monitor 1 |
| **Screenshot (Monitor 2)** | Capture and send monitor 2 |
| **Screenshot (All)** | Capture and send all monitors combined |
| **Webcam Photo** | Take a photo with the webcam on demand |
| **Memo Popup** | Display a styled fullscreen popup message on the PC screen |

### 📊 System Monitoring & Alerts
- **System Info** (`/sysinfo`): Real-time OS, CPU, RAM, Disk, and uptime report.
- **Top Processes** (`/top`): Top 5 by CPU and Top 5 by RAM usage.
- **Media Controls**: Play/Pause, Next Track, Previous Track.
- **Automated Background Alerts** (via monitoring thread):
  - ⚠️ CPU usage >90% for more than **5 minutes**
  - ⚠️ GPU temperature exceeds **80°C**

### 🔒 Security
- **Intruder Detection**: Captures a webcam photo automatically on startup and sends it to all admins.
- **Admin-only access**: A database-driven permission system ensures only authorized users can send commands.
- **Bot startup notification**: Admins receive a message whenever the bot comes online.

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.6+**
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- *(Optional)* A [Google Gemini API Key](https://aistudio.google.com/) for AI natural language features

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Configure the Bot

#### Option A — `.env` file *(Recommended)*
Copy `.env.example` to `.env` and fill in your values:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_here
GEMINI_TOKEN=your_gemini_api_key_here
CONSOLE_MODE=hide        # show | hide
STARTUP_ENABLED=false    # true | false
```

#### Option B — Setup Utility
Run the interactive setup wizard:
```powershell
python bot/bot_setup.py
```
- Enter your **BotFather Token**
- Enter your **Gemini Token** *(optional)*
- Add an **Admin** user (the first person to message the bot becomes an admin by default)

### 3. Run the Bot
```powershell
python bot/bot.pyw
```

### 4. Auto-start on Boot *(Windows)*
Double-click `install.bat` to register the bot in your Windows startup folder. If you ever move the project, run `install.bat` again to update the paths.

---

## 🛠️ Commands Reference

| Command | Description |
| --- | --- |
| `/start` | Start the bot / welcome message |
| `/help` | List all available commands |
| `/sysinfo` | OS, CPU, RAM, Disk, and uptime report |
| `/top` | Top 5 CPU and RAM consuming processes |
| `/screen1` | Screenshot of monitor 1 |
| `/screen2` | Screenshot of monitor 2 |
| `/screenall` | Screenshot of all monitors combined |
| `/webcam` | Capture a webcam photo |
| `/shutdown_h [hours]` | Schedule a shutdown after X hours |
| `/reboot` | Reboot the PC immediately |
| `/cancel` | Cancel a pending shutdown/reboot |
| `/launch [program]` | Launch a program by name |
| `/link [url]` | Open a URL in the browser |
| `/task_kill [process]` | Kill a running process by name |
| `/type [text]` | Type text on the PC keyboard |
| `/volume [0-100]` | Set system volume |
| `/brightness [0-100]` | Set screen brightness |
| `/lock` | Lock the PC screen |
| `/close` | Close the active window |
| `/minimize` | Minimize all windows (show desktop) |
| `/clipboard_get` | Read current clipboard text |
| `/memo [text]` | Show a popup message on screen |
| `/play_pause` | Media Play / Pause |
| `/next` | Media Next Track |
| `/prev` | Media Previous Track |
| `/empty_trash` | Empty the Recycle Bin |
| `/restart` | Restart the bot remotely |

---

## 📁 Project Structure

```
PC-Control-telegram-bot/
├── bot/
│   ├── bot.pyw          # Main bot logic
│   ├── bot_setup.py     # Interactive setup utility
│   ├── db.py            # Database layer (tokens, admins, settings)
│   └── utils.py         # Shared utilities
├── data/                # SQLite database (auto-created by setup)
├── tmp/                 # Temporary files (screenshots, webcam captures)
├── .env.example         # Environment variable template
├── install.bat          # Windows auto-start installer
├── install.py           # Installer script
├── requirements.txt     # Python dependencies
└── LICENSE
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
