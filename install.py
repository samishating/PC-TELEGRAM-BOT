import os
import platform
import sys

def create_startup_launcher():
    """
    Creates a .bat launcher in the Windows Startup folder to run the bot automatically.
    """
    if platform.system() != "Windows":
        print("This installation script is designed for Windows.")
        return

    # Get absolute paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    bot_script = os.path.join(project_root, "bot", "bot.pyw")
    
    # Check if bot.pyw exists, if not check for bot.py
    if not os.path.exists(bot_script):
        bot_script = os.path.join(project_root, "bot", "bot.py")
        if not os.path.exists(bot_script):
            print(f"Error: Could not find bot script at {os.path.join(project_root, 'bot', 'bot.pyw')}")
            return

    # Path to the Windows Startup folder (shell:startup)
    startup_path = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    launcher_path = os.path.join(startup_path, "PC-Control-Bot.bat")

    # Find the pythonw executable to run without a console window
    # sys.executable usually points to python.exe
    pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
    
    # If for some reason pythonw.exe isn't found in the same folder, fallback to 'pythonw'
    if not os.path.exists(pythonw_exe):
        pythonw_exe = "pythonw"

    # Create the batch file content
    # Using cd /d ensures the working directory is set to the project root
    launcher_content = f"""@echo off
rem Launcher for PC-Control Bot
cd /d "{project_root}"
start "" "{pythonw_exe}" "{bot_script}"
"""

    try:
        with open(launcher_path, "w") as f:
            f.write(launcher_content)
        print("-" * 50)
        print("Installation Successful!")
        print("-" * 50)
        print(f"Launcher created at: {launcher_path}")
        print("The bot will now start automatically when you log in.")
        print("-" * 50)
    except Exception as e:
        print(f"Failed to create startup launcher: {e}")

if __name__ == "__main__":
    create_startup_launcher()
