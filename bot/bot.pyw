#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import getpass
import logging
import os
import platform
import socket
import subprocess
import sys
import threading
from functools import wraps
from datetime import datetime
import webbrowser


# --- Global Silence Patch for Windows ---
if platform.system() == "Windows":
    class _SilentPopen(subprocess.Popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = 0x08000000
            else:
                kwargs['creationflags'] |= 0x08000000
            super().__init__(*args, **kwargs)
    subprocess.Popen = _SilentPopen
# ----------------------------------------

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    pass
from typing import Optional
from shlex import quote

import distro
import psutil
import mss
from telegram import ParseMode, ReplyKeyboardRemove, Update, Bot, BotCommand, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram import error as tg_error
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater, CallbackContext, CallbackQueryHandler
from telegram.utils import helpers

import db
import utils

# New dependencies
try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import sbc
except ImportError:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
except ImportError:
    AudioUtilities = None

import time

if sys.version_info < (3, 6, 0):
    raise Exception("This bot works only with Python 3.6+")

if db.exists() is False:
    raise Exception("You need to start bot_setup first")

def crash_handler(func):
    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            return func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            try:
                msg = f"⚠️ Crash in `{func.__name__}`: {str(e)}"
                if update and update.effective_chat:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            except:
                pass
    return wrapper

# Enable logging to both console and file
log_path = os.path.join(os.path.dirname(utils.current_path()), "bot.log")
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO, # Changed to INFO to reduce noise but kept it useful
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ])
logger = logging.getLogger(__name__)
logger.info("Bot script started")


def hide_console() -> None:
    if platform.system() == "Windows":
        if db.console_get() == "hide":
            # SW_HIDE = 0
            # Force hide the console window multiple times to ensure it's caught
            con = ctypes.windll.kernel32.GetConsoleWindow()
            if con:
                ctypes.windll.user32.ShowWindow(con, 0)


def startupinfo() -> Optional[subprocess.STARTUPINFO]:
    if db.console_get() == "hide":
        if platform.system() == "Windows":
            value = subprocess.STARTUPINFO()
            value.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            value.wShowWindow = 0  # SW_HIDE
        else:
            value = None
    else:
        value = None
    return value


@crash_handler
def start(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = r"""Welcome to *PC\-Control AI*\! 🤖✨

I am now powered by *Gemini Pro*, which means you can control your PC using natural language\.

Try saying:
• _"Turn off the computer in 1 hour"_
• _"Show my desktop"_
• _"Lock the screen"_

You can also chat with me normally or use /help to see the classic command list\.

Ready to help you control your world\!"""

    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true",
        reply_markup=ReplyKeyboardRemove())


@crash_handler
@db.admin_check
def bot_help(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    text = "*Available commands:*"
    text += helpers.escape_markdown("""
/shutdown_h - To shutdown your PC after X hours
/reboot - To reboot your PC
/cancel - To annul the previous command
/launch - To launch a program
/link - To open a link
/memo - To show a memo on your pc
/task_kill - To kill a specific process
/top - To list the top 5 resource-consuming tasks
/restart - To restart the bot
/screen1 - To take a screenshot of the 1st monitor
/screen2 - To take a screenshot of the 2nd monitor
/screenall - To take a screenshot of all monitors
/type - To type text on the PC keyboard
/volume - To set the volume (0-100)
/brightness - To set screen brightness (0-100)
/lock - To lock the PC screen
/close - To close the active window
/sysinfo - To get system statistics
/clipboard_get - To get PC clipboard text
/play_pause - Media Play/Pause
/next - Media Next Track
/prev - Media Previous Track
/empty_trash - Clear the Recycle Bin
/minimize - Minimize all windows
""", 2)
    context.bot.send_message(
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview="true")


def get_gemini_response(text: str) -> Optional[str]:
    if not genai:
        return None
    
    api_key = db.token_get("Gemini_token")
    if not api_key:
        return None
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-flash-latest')
        
        system_prompt = """You are a PC-Control AI Assistant. You help users control their PC using natural language. 
Below is a list of available commands and their purpose:
- /shutdown_h [hours]: Shutdown PC after X hours.
- /reboot: Reboot PC.
- /cancel: Cancel shutdown/reboot.
- /launch [program]: Launch a program.
- /link [url]: Open a link.
- /memo [text]: Show a memo on screen.
- /task_kill [process]: Kill a process.
- /top: List top processes.
- /screen1: Screenshot monitor 1.
- /screen2: Screenshot monitor 2.
- /screenall: Screenshot all monitors.
- /type [text]: Type text on PC.
- /volume [0-100]: Set volume.
- /brightness [0-100]: Set brightness.
- /lock: Lock PC.
- /close: Close active window.
- /sysinfo: Get system stats.
- /clipboard_get: Get clipboard text.
- /play_pause: Media Play/Pause.
- /next: Media Next.
- /prev: Media Previous.
- /empty_trash: Empty recycle bin.
- /minimize: Minimize all windows.

If the user wants to perform one of these actions, respond EXCLUSIVELY with 'COMMAND: ' followed by the command and its arguments. 
Example: User says 'turn off in 1 hour', you respond 'COMMAND: /shutdown_h 1'.
If the user's request doesn't match a command, respond with a helpful message as a regular AI assistant."""

        response = model.generate_content(f"{system_prompt}\n\nUser: {text}")
        
        if not response.candidates:
             logger.warning("Gemini returned no candidates (possible block)")
             return None

        try:
            return response.text
        except ValueError:
            # If the response was blocked, we can't access the text
            logger.warning("Could not access response.text (possibly blocked)")
            return None

    except Exception as e:
        logger.error(f"Gemini error: {e}", exc_info=True)
        return None


@crash_handler
def message_handler(update: Update, context: CallbackContext) -> None:
    if update.message.reply_to_message:
        handle_reply(update, context)
    elif update.message.text:
        text = update.message.text
        logger.info(f"Received message: {text}")
        if text == "Exit":
            pass
        else:
            # Let User know we are processing
            # msg = update.message.reply_text("Thinking...")
            
            # Let Gemini handle it
            response = get_gemini_response(text)
            # context.bot.delete_message(chat_id=update.message.chat.id, message_id=msg.message_id)

            if response:
                if response.startswith("COMMAND:"):
                    # ... (rest of the command processing)
                    cmd_part = response[len("COMMAND:"):].strip()
                    parts = cmd_part.split(maxsplit=1)
                    command = parts[0]
                    args = parts[1] if len(parts) > 1 else ""
                    
                    # Store args in context
                    context.args = args.split() if args else []
                    
                    # Map of command strings to functions
                    cmd_map = {
                        "/shutdown_h": shutdown_h,
                        "/reboot": reboot,
                        "/cancel": cancel,
                        "/launch": launch,
                        "/link": link,
                        "/memo": memo_thread,
                        "/task_kill": task_kill,
                        "/top": top_processes,
                        "/screen1": screenshot1,
                        "/screen2": screenshot2,
                        "/screenall": screenshot_all,
                        "/type": type_text,
                        "/volume": volume,
                        "/brightness": brightness,
                        "/lock": lock_screen,
                        "/close": close_window,
                        "/sysinfo": system_info,
                        "/clipboard_get": clipboard_get,
                        "/play_pause": media_play_pause,
                        "/next": media_next,
                        "/prev": media_prev,
                        "/empty_trash": empty_trash,
                        "/minimize": minimize_all,
                        "/restart": restart_bot
                    }
                    
                    if command in cmd_map:
                        # Log the interpreted command
                        logger.info(f"NLP interpreted: {text} -> {command} {args}")
                        cmd_map[command](update, context)
                    else:
                        update.message.reply_text(f"Gemini suggested an unknown command: {command}")
                else:
                    update.message.reply_text(response)
            else:
                # If Gemini fails or isn't configured, we just ignore or could do something else
                pass


@crash_handler
def handle_reply(update: Update, context: CallbackContext) -> None:
    original_text = update.message.reply_to_message.text
    content = update.message.text
    context.args = [content]
    
    if "number of hours" in original_text:
        if "shutdown" in original_text:
            shutdown_time_h(update, context)
        elif "reboot" in original_text:
            reboot_time(update, context)
    elif "Insert the link" in original_text:
        link(update, context)
    elif "Insert the name of the program" in original_text:
        launch(update, context)
    elif "Insert the name of the process to kill" in original_text:
        task_kill(update, context)
    elif "Insert the text for the memo" in original_text:
        memo_thread(update, context)
    elif "Insert the text to type on the PC:" in original_text:
        type_text(update, context)
    elif "Insert the volume percentage (0-100):" in original_text:
        volume(update, context)
    elif "Insert the brightness percentage (0-100):" in original_text:
        brightness(update, context)




@crash_handler
@db.admin_check
def shutdown_h(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        shutdown_time_h(update, context)
    else:
        text = "Insert the number of hours for the shutdown:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def shutdown_time_h(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        try:
            hours = float(context.args[0])
            seconds = int(hours * 3600)
            if platform.system() == "Windows":
                subprocess.run(f"shutdown /s /t {seconds}",
                               startupinfo=startupinfo())
                text = f"Shutting down in {hours} hours..."
                context.bot.send_message(chat_id=update.message.chat.id, text=text)
            else:
                # Linux shutdown -P +minutes
                minutes = int(hours * 60)
                subprocess.run(f"shutdown -P +{minutes}",
                               startupinfo=startupinfo(), shell=True)
                text = f"Shutting down in {hours} hours..."
                context.bot.send_message(chat_id=update.message.chat.id, text=text)
        except ValueError:
            context.bot.send_message(chat_id=update.message.chat.id, text="Please insert a valid number.")
    else:
        text = "Insert the number of hours for the shutdown:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def reboot(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if platform.system() == "Windows":
        subprocess.run('shutdown /r', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.send_message(chat_id=update.message.chat.id, text=text)
    else:
        subprocess.run('reboot', startupinfo=startupinfo())
        text = "Rebooted."
        context.bot.send_message(chat_id=update.message.chat.id, text=text)


@crash_handler
@db.admin_check
def reboot_time(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            subprocess.run(f"shutdown /r /t {str(int(context.args[0])*60)}",
                           startupinfo=startupinfo())
            text = "Rebooting..."
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
        else:
            subprocess.run(f"shutdown -r +{quote(context.args[0])}",
                           startupinfo=startupinfo(), shell=True)
            text = "Rebooting..."
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
    else:
        text = "Insert the number of minutes for the reboot:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))




@crash_handler
@db.admin_check
def cancel(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if (thread_name := utils.ThreadTimer().stop()):
        text = f"{thread_name} cancelled"
    else:
        text = "Annulled."
        if platform.system() == "Windows":
            subprocess.run('shutdown /a', startupinfo=startupinfo())
        else:
            subprocess.run('shutdown -c', startupinfo=startupinfo(), shell=True)
    context.bot.send_message(chat_id=update.message.chat.id, text=text)



@crash_handler
@db.admin_check
def clipboard_get(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if not pyperclip:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'pyperclip' library is not installed.")
        return
    try:
        text = pyperclip.paste()
        if text:
            # Telegram message limit is 4096. 
            # We'll truncate and escape it properly for MarkdownV2.
            if len(text) > 3900:
                text = text[:3900] + "..."
            
            # Using code block for better readability
            escaped_text = helpers.escape_markdown(text, version=2)
            msg = f"📋 *PC Clipboard Content:*\n\n`{escaped_text}`"
            context.bot.send_message(chat_id=update.message.chat.id, text=msg, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Clipboard is empty or contains non-text data.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error getting clipboard: {e}")


@crash_handler
@db.admin_check
def type_text(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if not pyautogui or not pyperclip:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'pyautogui' and 'pyperclip' libraries are required.")
        return
    
    if context.args:
        text_to_type = " ".join(context.args)
        try:
            # Check if text is pure ASCII
            try:
                text_to_type.encode('ascii')
                is_ascii = True
            except UnicodeEncodeError:
                is_ascii = False
            
            if is_ascii:
                # Fast direct typing for ASCII
                pyautogui.write(text_to_type)
                context.bot.send_message(chat_id=update.message.chat.id, text="Text typed (Direct ASCII mode).")
            else:
                # Optimized clipboard paste for Unicode (Arabic etc.)
                original_clipboard = ""
                try:
                    original_clipboard = pyperclip.paste()
                except Exception:
                    pass
                
                pyperclip.copy(text_to_type)
                time.sleep(0.1) # Wait for clipboard
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.1) # Wait for paste
                
                # Restore original clipboard with slight delay
                try:
                    if original_clipboard:
                        pyperclip.copy(original_clipboard)
                    else:
                        pyperclip.copy('')
                except Exception:
                    pass
                context.bot.send_message(chat_id=update.message.chat.id, text="Text typed (Fuzzy Unicode mode).")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Error typing text: {e}")
    else:
        text = "Insert the text to type on the PC:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def volume(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if AudioUtilities is None:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'pycaw' library is not installed or failed to load.")
        return

    if context.args:
        try:
            level = int(context.args[0])
            if level < 0 or level > 100:
                raise ValueError
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
            volume_ctrl.SetMasterVolumeLevelScalar(level / 100.0, None)
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Volume set to {level}%")
                
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Error setting volume: {e}")
    else:
        text = "Insert the volume percentage (0-100):"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def brightness(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if sbc is None:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'screen-brightness-control' is not installed.")
        return
    
    if context.args:
        try:
            level = int(context.args[0])
            if 0 <= level <= 100:
                sbc.set_brightness(level)
                context.bot.send_message(chat_id=update.message.chat.id, text=f"Brightness set to {level}%")
            else:
                context.bot.send_message(chat_id=update.message.chat.id, text="Value must be between 0 and 100.")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Error setting brightness: {e}")
    else:
        text = "Insert the brightness percentage (0-100):"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def media_play_pause(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if pyautogui:
            pyautogui.press('playpause')
            context.bot.send_message(chat_id=update.message.chat.id, text="Media Play/Pause signal sent.")
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'pyautogui' not installed")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def media_next(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if pyautogui:
            pyautogui.press('nexttrack')
            context.bot.send_message(chat_id=update.message.chat.id, text="Media Next signal sent.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def media_prev(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if pyautogui:
            pyautogui.press('prevtrack')
            context.bot.send_message(chat_id=update.message.chat.id, text="Media Previous signal sent.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def empty_trash(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if platform.system() == "Windows":
            subprocess.run(["powershell.exe", "-Command", "Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], startupinfo=startupinfo())
            context.bot.send_message(chat_id=update.message.chat.id, text="Recycle Bin emptied.")
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Not implemented for this OS.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def minimize_all(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if pyautogui:
            pyautogui.hotkey('win', 'd')
            context.bot.send_message(chat_id=update.message.chat.id, text="Desktop shown (all minimized).")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def close_window(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if pyautogui:
            pyautogui.hotkey('alt', 'f4')
            context.bot.send_message(chat_id=update.message.chat.id, text="Active window closed.")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def system_info(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        
        # Aggressively escape every piece of dynamic data
        esc_os = helpers.escape_markdown(f"{platform.system()} {platform.release()}", 2)
        esc_cpu = helpers.escape_markdown(f"{cpu}%", 2)
        esc_ram = helpers.escape_markdown(f"{ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)", 2)
        esc_disk = helpers.escape_markdown(f"{disk.percent}% used", 2)
        esc_boot = helpers.escape_markdown(boot_time, 2)
        
        text = "*System Information*\n"
        text += f"🖥️ *OS:* {esc_os}\n"
        text += f"🔥 *CPU:* {esc_cpu}\n"
        text += f"🧠 *RAM:* {esc_ram}\n"
        text += f"💾 *Disk:* {esc_disk}\n"
        text += f"⏱️ *Up since:* {esc_boot}"
        
        try:
            context.bot.send_message(chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
        except Exception:
            # Fallback to plain text if MarkdownV2 still fails
            plain_text = text.replace('*', '').replace('\\', '')
            context.bot.send_message(chat_id=update.message.chat.id, text=plain_text)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error getting system info: {e}")


@crash_handler
@db.admin_check
def lock_screen(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    try:
        if platform.system() == "Windows":
            ctypes.windll.user32.LockWorkStation()
            text = "PC locked."
        else:
            # Common Linux lock commands
            subprocess.run("xdg-screensaver lock", shell=True)
            text = "Lock signal sent."
        context.bot.send_message(chat_id=update.message.chat.id, text=text)
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error locking PC: {e}")


@crash_handler
@db.admin_check
def screenshot_all(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    path = os.path.join(os.path.dirname(utils.current_path()), "tmp/screenshot_all.png")
    try:
        with mss.mss() as sct:
            sct.shot(mon=0, output=path)
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                context.bot.send_document(chat_id=update.message.chat.id, document=f)
            os.remove(path)
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Error: Failed to capture all screens")
    except Exception as e:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {e}")


@crash_handler
@db.admin_check
def top_processes(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            # Ensure values are not None for sorting
            if pinfo['cpu_percent'] is None: pinfo['cpu_percent'] = 0.0
            if pinfo['memory_percent'] is None: pinfo['memory_percent'] = 0.0
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Top 5 CPU
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
    # Top 5 Memory
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]

    text = "*Top 5 CPU Consuming Tasks:*\n"
    for p in top_cpu:
        name = helpers.escape_markdown(str(p['name']), 2)
        pid = helpers.escape_markdown(str(p['pid']), 2)
        cpu = helpers.escape_markdown(f"{p['cpu_percent']}%", 2)
        # Manually escape characters outside the variables
        text += f"• `{name}` \(PID: `{pid}`\): `{cpu}` CPU\n"
    
    text += "\n*Top 5 Memory Consuming Tasks:*\n"
    for p in top_mem:
        name = helpers.escape_markdown(str(p['name']), 2)
        pid = helpers.escape_markdown(str(p['pid']), 2)
        mem = helpers.escape_markdown(f"{p['memory_percent']:.1f}%", 2)
        text += f"• `{name}` \(PID: `{pid}`\): `{mem}` RAM\n"

    try:
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        logger.error(f"Markdown error in /top: {e}")
        # Fallback to plain text if Markdown fails
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text=text.replace('*', '').replace('`', '').replace('\\', ''))


@crash_handler
@db.admin_check
def restart_bot(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    context.bot.send_message(chat_id=update.message.chat.id, text="Bot is restarting...")
    
    def restart():
        time.sleep(1)
        if platform.system() == "Windows":
            # On Windows, os.execv doesn't always work as expected with certain setups
            # Using subprocess to start a new process and then exiting current one
            subprocess.Popen([sys.executable] + sys.argv)
            os._exit(0)
        else:
            os.execv(sys.executable, ['python'] + sys.argv)
            
    threading.Thread(target=restart).start()


@crash_handler
@db.admin_check
def launch(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        if platform.system() == "Windows":
            ret = subprocess.run(f"start {quote(context.args[0])}",
                                 startupinfo=startupinfo(), shell=True).returncode
            text = f"Launching {context.args[0]}..." if ret == 0 else f"Cannot launch {context.args[0]}"
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
        else:
            ret = subprocess.run(f"{str(quote(context.args[0]))} &",
                    startupinfo=startupinfo(), shell=True).returncode
            text = f"Launching {context.args[0]}..." if ret == 0 else f"Cannot launch {context.args[0]}"
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
    else:
        text = "Insert the name of the program to launch:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def link(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        url = context.args[0]
        # Common fix for URLs without protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            webbrowser.open(url)
            text = f"Opening {url}..."
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
        except Exception as e:
            text = f"Cannot open {url}: {e}"
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
    else:
        text = "Insert the link to open:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def memo_thread(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    module = "tkinter"
    if module not in sys.modules:
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: you need to install {module} to use this function")

    if context.args:
        args = " ".join(context.args)
    else:
        # Fallback for replies or if context.args is somehow missing
        args = update.message.text.replace("/memo", "").strip()
        if not args and hasattr(update.message, 'reply_to_message') and update.message.reply_to_message:
            args = update.message.text.strip()

    if args:
        def memo() -> None:
            try:
                popup = tk.Tk()
            
                # Remove title bar
                popup.overrideredirect(True)
                
                # Set fixed size
                width, height = 800, 500
                
                # Center on screen
                screen_width = popup.winfo_screenwidth()
                screen_height = popup.winfo_screenheight()
                x = (screen_width // 2) - (width // 2)
                y = (screen_height // 2) - (height // 2)
                popup.geometry(f"{width}x{height}+{x}+{y}")
                
                # Always on top
                popup.attributes("-topmost", True)
                
                # Use a frame for the border (2px "Bazouya" orange/accent blue)
                # Orange hex: #FF8C00 (Accent orange)
                main_frame = tk.Frame(popup, bg="black", highlightthickness=2, highlightbackground="#FF8C00")
                main_frame.pack(fill="both", expand=True)
                
                # Container for content with internal padding
                content_frame = tk.Frame(main_frame, bg="black")
                content_frame.pack(fill="both", expand=True, padx=50, pady=50)
                
                label_text = f"{args}\n\nSent by {update.message.from_user.name}"
                
                label = tk.Label(
                    content_frame,
                    text=label_text,
                    fg="white",
                    bg="black",
                    font=("Helvetica", 36),
                    wraplength=700,
                    justify="center"
                )
                label.pack(expand=True)
                
                # Close instruction
                close_hint = tk.Label(
                    content_frame,
                    text="Click anywhere to close",
                    fg="#666666",
                    bg="black",
                    font=("Helvetica", 10)
                )
                close_hint.pack(side="bottom", pady=(20, 0))
                
                # Close on click
                popup.bind("<Button-1>", lambda e: popup.destroy())
                main_frame.bind("<Button-1>", lambda e: popup.destroy())
                content_frame.bind("<Button-1>", lambda e: popup.destroy())
                label.bind("<Button-1>", lambda e: popup.destroy())
                
                popup.mainloop()
            except Exception as e:
                logger.error(f"Error in memo thread: {e}", exc_info=True)
                try:
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"⚠️ Crash in memo visualizer: {str(e)}"
                    )
                except Exception:
                    pass

        t = threading.Thread(target=memo)
        t.start()
    else:
        text = "Insert the text for the memo:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))



@crash_handler
@db.admin_check
def task_kill(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if context.args:
        args = " ".join(context.args)
        try:
            matches = []
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    if p.info['name'] and args.lower() in p.info['name'].lower():
                        matches.append(p)
                except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError, AttributeError):
                    pass
                    
            if matches:
                killed = []
                for match in matches:
                    try:
                        proc = psutil.Process(match.info['pid'])
                        # Kill children
                        for child in proc.children(recursive=True):
                            try:
                                child.kill()
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        proc.kill()
                        killed.append(match.info['name'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if killed:
                    killed_unique = list(set(killed))
                    text = f"I've successfully killed:\n" + "\n".join(f"- {name}" for name in killed_unique)
                else:
                    text = f"Found matches for '{args}', but couldn't kill them. Check permissions."
            else:
                text = f"No process found matching '{args}'."
                
            context.bot.send_message(chat_id=update.message.chat.id, text=text)
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Error: {str(e)}")
    else:
        text = "Insert the name of the process to kill:"
        update.message.reply_text(text, reply_markup=ForceReply(selective=True))


@crash_handler
@db.admin_check
def screenshot1(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    path = os.path.join(os.path.dirname(utils.current_path()), "tmp/screenshot1.png")
    try:
        with mss.mss() as sct:
            # Monitor 1 is at index 1 (index 0 is the combination of all monitors)
            if len(sct.monitors) < 2:
                context.bot.send_message(chat_id=update.message.chat.id, text="Error: Monitor 1 not found")
                return
            sct.shot(mon=1, output=path)
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                context.bot.send_document(chat_id=update.message.chat.id, document=f)
            os.remove(path)
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Error: Failed to capture screenshot1")
    except Exception as e:
        logger.error(f"Screenshot1 error: {e}")
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error taking screen1 screenshot: {e}")


@crash_handler
@db.admin_check
def screenshot2(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    path = os.path.join(os.path.dirname(utils.current_path()), "tmp/screenshot2.png")
    try:
        with mss.mss() as sct:
            # Monitor 2 is at index 2
            if len(sct.monitors) < 3:
                context.bot.send_message(chat_id=update.message.chat.id, text="Error: Monitor 2 not found")
                return
            sct.shot(mon=2, output=path)
        
        if os.path.exists(path):
            with open(path, "rb") as f:
                context.bot.send_document(chat_id=update.message.chat.id, document=f)
            os.remove(path)
        else:
            context.bot.send_message(chat_id=update.message.chat.id, text="Error: Failed to capture screenshot2")
    except Exception as e:
        logger.error(f"Screenshot2 error: {e}")
        context.bot.send_message(chat_id=update.message.chat.id, text=f"Error taking screen2 screenshot: {e}")


def capture_webcam() -> Optional[str]:
    if not cv2:
        logger.warning("cv2 (OpenCV) not installed, skipping webcam capture.")
        return None
    path = os.path.join(os.path.dirname(utils.current_path()), "tmp/intruder.jpg")
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        # Give some time to warm up
        time.sleep(2)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(path, frame)
        cap.release()
        return path if os.path.exists(path) else None
    except Exception as e:
        logger.error(f"Webcam error: {e}")
        return None


@crash_handler
@db.admin_check
def manual_webcam(update: Update, context: CallbackContext) -> None:
    db.update_user(update.message.from_user, context.bot)
    if not cv2:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: 'opencv-python' library is not installed.")
        return
    
    context.bot.send_message(chat_id=update.message.chat.id, text="Capturing photo...")
    photo_path = capture_webcam()
    if photo_path:
        try:
            with open(photo_path, "rb") as f:
                context.bot.send_photo(chat_id=update.message.chat.id, photo=f, caption="Manual Webcam Capture")
            os.remove(photo_path)
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat.id, text=f"Error sending photo: {e}")
    else:
        context.bot.send_message(chat_id=update.message.chat.id, text="Error: Failed to capture webcam photo. Ensure the camera is connected and not in use by another app.")


class MonitorThread(threading.Thread):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.daemon = True
        self.cpu_high_start = None

    def run(self):
        while True:
            try:
                admins = db.get_admins_id()
                # CPU Monitor
                cpu_usage = psutil.cpu_percent()
                if cpu_usage > 90:
                    if self.cpu_high_start is None:
                        self.cpu_high_start = time.time()
                    elif time.time() - self.cpu_high_start > 300:  # 5 minutes
                        for admin_id in admins:
                            self.bot.send_message(chat_id=admin_id, text=f"⚠️ ALERT: CPU usage has been at {cpu_usage}% for over 5 minutes!")
                        self.cpu_high_start = None # Reset to avoid spam
                else:
                    self.cpu_high_start = None

                # GPU Monitor
                if GPUtil:
                    gpus = GPUtil.getGPUs()
                    for gpu in gpus:
                        if gpu.temperature > 80:
                            for admin_id in admins:
                                self.bot.send_message(chat_id=admin_id, text=f"⚠️ ALERT: GPU {gpu.name} temperature is high: {gpu.temperature}°C!")



            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            
            time.sleep(60)





# ──────────────────────────────────────────────────────────────────────────────


def is_up_notification(bot: Bot) -> None:
    admins = db.get_admins_id()
    for admin_id in admins:
        bot.send_message(chat_id=admin_id, text="Bot up and running")
    

def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")


def main() -> None:
    # Create the EventHandler and pass it your bot's token.
    if not db.token_get("BotFather_token"):
        raise ValueError("You need to add a BotFather token first")

    updater = Updater(db.token_get("BotFather_token"))

    # Set bot commands (Alphabetized)
    updater.bot.set_my_commands([
        BotCommand("brightness", "Set PC brightness (0-100)"),
        BotCommand("cancel", "Cancel the previous command"),
        BotCommand("clipboard_get", "Get PC clipboard content"),
        BotCommand("close", "Close the active window"),
        BotCommand("empty_trash", "Empty Recycle Bin"),
        BotCommand("help", "List all commands"),
        BotCommand("launch", "Launch a program"),
        BotCommand("link", "Open a link"),
        BotCommand("lock", "Lock the PC screen"),
        BotCommand("memo", "Show a memo on PC screen"),
        BotCommand("minimize", "Minimize all windows"),
        BotCommand("next", "Media Next Track"),
        BotCommand("play_pause", "Media Play/Pause"),
        BotCommand("prev", "Media Previous Track"),
        BotCommand("reboot", "Reboot the PC"),
        BotCommand("restart", "Restart the bot remotely"),
        BotCommand("screen1", "Take a screenshot of monitor 1"),
        BotCommand("screen2", "Take a screenshot of monitor 2"),
        BotCommand("screenall", "Take a screenshot of all monitors"),
        BotCommand("shutdown_h", "Shutdown after X hours"),
        BotCommand("start", "Start the bot"),
        BotCommand("sysinfo", "Show PC statistics"),
        BotCommand("task_kill", "Kill a process"),
        BotCommand("top", "Top 5 resource eating tasks"),
        BotCommand("type", "Type text on PC keyboard"),
        BotCommand("volume", "Set PC volume (0-100)"),
        BotCommand("webcam", "Take a photo with the webcam")
    ])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Hide console if requested
    hide_console()

    # Send a message when the bot is up and running
    is_up_notification(updater.bot)

    # Start
    dp.add_handler(CommandHandler("start", start))

    # Help
    dp.add_handler(CommandHandler("help", bot_help))

    # Shutdown hours
    dp.add_handler(CommandHandler(
        "shutdown_h", shutdown_h, pass_args=True))

    # Shutdown hours time
    dp.add_handler(CommandHandler(
        "shutdown_h_t", shutdown_time_h, pass_args=True))

    # Reboot
    dp.add_handler(CommandHandler("reboot", reboot))

    # Reboot time
    dp.add_handler(CommandHandler(
        "reboot_t", reboot_time, pass_args=True))

    # Annul the previous command
    dp.add_handler(CommandHandler("cancel", cancel))

    # Launch a program
    dp.add_handler(CommandHandler("launch", launch, pass_args=True))

    # Open a link with the default browser
    dp.add_handler(CommandHandler("link", link, pass_args=True))

    # Show a popup with the memo
    dp.add_handler(CommandHandler("memo", memo_thread, pass_args=True))

    # Kill the selected process
    dp.add_handler(CommandHandler("task_kill", task_kill, pass_args=True))

    # Send a screenshot of monitor 1
    dp.add_handler(CommandHandler("screen1", screenshot1))

    # Send a screenshot of monitor 2
    dp.add_handler(CommandHandler("screen2", screenshot2))

    # Send a screenshot of all monitors
    dp.add_handler(CommandHandler("screenall", screenshot_all))

    # Send a photo with the webcam
    dp.add_handler(CommandHandler("webcam", manual_webcam))

    # Top processes
    dp.add_handler(CommandHandler("top", top_processes))

    # Restart bot
    dp.add_handler(CommandHandler("restart", restart_bot))

    # Clipboard
    dp.add_handler(CommandHandler("clipboard_get", clipboard_get))

    # Type on keyboard
    dp.add_handler(CommandHandler("type", type_text, pass_args=True))

    # Volume control
    dp.add_handler(CommandHandler("volume", volume, pass_args=True))

    # Brightness control
    dp.add_handler(CommandHandler("brightness", brightness, pass_args=True))

    # Lock screen
    dp.add_handler(CommandHandler("lock", lock_screen))

    # Close active window
    dp.add_handler(CommandHandler("close", close_window))

    # System Info
    dp.add_handler(CommandHandler("sysinfo", system_info))

    # Media Controls
    dp.add_handler(CommandHandler("play_pause", media_play_pause))
    dp.add_handler(CommandHandler("next", media_next))
    dp.add_handler(CommandHandler("prev", media_prev))

    # Other Utilities
    dp.add_handler(CommandHandler("empty_trash", empty_trash))
    dp.add_handler(CommandHandler("minimize", minimize_all))

    # Start monitor thread
    MonitorThread(updater.bot).start()

    # Keyboard Button Reply
    dp.add_handler(MessageHandler(Filters.text |
                                  Filters.status_update, message_handler))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
