<img src="https://user-images.githubusercontent.com/25140297/177854111-c6c7e75f-4dce-4255-a157-2c9dd1faad50.png#gh-light-mode-only" alt="logo" width="100"/>
<img src="https://user-images.githubusercontent.com/25140297/177854228-9b60703c-5821-42d5-b1a0-134289b59442.png#gh-dark-mode-only" alt="logo" width="100"/>

# PC Control bot

Through this bot you can execute actions on your PC directly from Telegram!

## Getting Started

### Prerequisites

- Python 3.6+
- A [BotFather](https://t.me/BotFather) token

GNU/Linux users: to use UI features (setup with UI and memo) you need to install the python-tk package

### Install the requirements
Execute ```python -m pip install -r requirements.txt```

## Setup the bot
### UI 
Launch the setup with ```python bot/bot_setup.py```

Add your BotFather token and start it!

![setup](https://user-images.githubusercontent.com/25140297/103703845-95b99680-4fa8-11eb-9b09-b660760de701.png)

### Command line 
You can also setup the bot from the command line by using ```python bot/bot_setup.py``` followed by a valid option.\
To see all the available options use ```python bot/bot_setup.py -h```

## Set the permissions

**The first user registered into the database will have admin permissions by default.** \
You can add or remove a user from the admin group by using the UI or the command line.\
**Note:** you need to use a Telegram username (write it without '@') 

UI example:

![privs](https://user-images.githubusercontent.com/25140297/103581006-76086c80-4edb-11eb-99a4-4e13777e7794.png)

## Available commands

| Command | Description | Note
| --- | --- | --- |
| /shutdown_h | Shutdown your PC after X hours | Use `/shutdown_h [hours]` |
| /reboot | Reboot your PC | Use `/reboot_t [min]` for delayed reboot |
| /cancel | Annul the previous command | Stops pending timers |
| /check | Check the PC status | CPU, RAM, Battery, etc. | 
| /launch | Launch a program | Interactive prompt enabled |
| /link | Open a web link | |
| /memo | Show a memo on your pc | Tkinter needed |
| /task | Check if a process is running | Interactive prompt enabled |
| /task_kill | Kill a specific process | Interactive prompt enabled |
| /top | List top 5 resource-consuming tasks | CPU and Memory |
| /clipboard_get | Get current PC clipboard text | |
| /screen1 | Take a screenshot of monitor 1 | |
| /screen2 | Take a screenshot of monitor 2 | |
| /webcam | Take a photo with the webcam | |
| /restart | Restart the bot remotely | |

### Interactive Prompts
Commands like `/launch`, `/link`, `/task`, and `/shutdown_h` now support interactive prompts.

### Advanced Features
- **Custom Threshold Alerts**: The bot automatically monitors your system and alerts you if:
    - CPU usage is >90% for more than 5 minutes.
    - GPU temperature exceeds 80°C.
    - Disk space is <10% free.
- **Intruder Detection**: Every time the bot starts (e.g., on PC power-on), it captures a photo using the webcam and sends it to the admin.
- **Remote Clipboard**: Use `/clipboard_get` to retrieve your PC's clipboard content.

## Push to your GitHub

If you want to push these updates to your own GitHub repository:

1. **Initialize Git (if not already):**
   ```powershell
   git init
   ```

2. **Add your files:**
   ```powershell
   git add .
   ```

3. **Commit the changes:**
   ```powershell
   git commit -m "Update bot features and documentation"
   ```

4. **Add your remote repository:**
   (Replace the URL with your own GitHub repository URL)
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

5. **Push to GitHub:**
   ```powershell
   git push -u origin master
   ```

## Contributors
Thanks to [Jasoc](https://github.com/jasoc) for the awesome [logo](https://i.imgur.com/V6B5ZEf.png)!
