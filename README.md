# 🤖 PC-Control Telegram Bot

Control your PC remotely from anywhere in the world using Telegram! This bot allows you to monitor system status, execute commands, capture media, and automate security tasks directly from your phone.

---

## ✨ Key Features

### 🖥️ Remote Control
- **System Actions**: Shutdown, Reboot, and Cancel timers remotely.
- **Program Management**: Launch applications and kill running processes.
- **Web Navigation**: Open any web link on your PC.
- **Clipboard**: Retrieve the current text from your PC's clipboard.

### 📊 System Monitoring
- **Status Check**: Real-time reports on CPU usage, RAM, Battery, and Disk space.
- **Performance**: View the top 5 resource-consuming tasks.
- **Automated Alerts**: Receive notifications if:
    - CPU usage is >90% for more than 5 minutes.
    - GPU temperature exceeds 80°C.
    - Disk space falls below 10% free.

### 📸 Media & Security
- **Screenshots**: Capture high-quality screenshots of all connected monitors.
- **Webcam**: Take photos using the system's webcam.
- **Intruder Detection**: Automatically captures a photo and notifies you every time the PC starts up.
- **Memos**: Display pop-up messages on the PC screen.

### 🧠 Advanced Capabilities
- **Gemini AI Integration**: Leverages Google's Gemini AI for enhanced interactions.
- **Interactive Prompts**: User-friendly prompts for complex commands like `/launch` and `/task`.

---

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.6+** installed on your system.
- A Telegram bot token from [@BotFather](https://t.me/BotFather).
- (Optional) A [Gemini AI API Key](https://aistudio.google.com/) for AI features.

### 2. Install Dependencies
Open your terminal in the project folder and run:
```powershell
pip install -r requirements.txt
```

### 3. Quick Install (Windows)
To set up the bot to **start automatically** when your computer boots:
1. Double-click `install.bat`.
2. This will create a dynamic launcher in your `shell:startup` folder.
3. **Note**: If you ever move this project folder to a new location, simply run `install.bat` again to update the paths automatically.

### 4. Configuration
Launch the setup utility to configure your tokens and permissions:
```powershell
python bot/bot_setup.py
```
- Enter your **BotFather Token**.
- Enter your **Gemini Token** (optional).
- Add yourself as an **Admin** (the first user to message the bot will become an admin by default).

---

## 🛠️ Commands Reference

| Command | Description |
| --- | --- |
| `/check` | Comprehensive system health report |
| `/screen1` / `/screen2` | Capture monitor screenshots |
| `/webcam` | Take a photo via webcam |
| `/shutdown_h [hours]` | Schedule a shutdown |
| `/reboot` | Restart the PC immediately |
| `/launch` | Start a specific program |
| `/task` | Check if a process is running |
| `/clipboard_get` | Get text from PC clipboard |
| `/memo` | Show a message box on screen |
| `/restart` | Restart the bot itself |

---

## 🔒 Security
The bot implements a database-driven permission system. Only authorized administrators can execute sensitive commands. You can manage permissions via the `bot_setup.py` UI or CLI.

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
