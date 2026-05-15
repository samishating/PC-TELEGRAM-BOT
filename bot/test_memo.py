import unittest
from unittest.mock import MagicMock
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock dependencies before importing bot
sys.modules['telegram'] = MagicMock()
sys.modules['telegram.ext'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['psutil'] = MagicMock()
sys.modules['pyautogui'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()
sys.modules['sbc'] = MagicMock()
sys.modules['GPUtil'] = MagicMock()
sys.modules['pycaw.pycaw'] = MagicMock()
sys.modules['genai'] = MagicMock()

import bot

class TestMemo(unittest.TestCase):
    def test_memo_thread_args(self):
        # We want to test how memo_thread handles arguments
        update = MagicMock()
        context = MagicMock()
        
        # Scenario 1: command sent directly
        update.message.text = "/memo this is a test"
        context.args = ["this", "is", "a", "test"]
        
        bot.memo_thread(update, context)
        
        # How to capture the args?
        # We can mock threading.Thread to see what target is started and what variables it closure captures
        # But maybe we can just patch tkinter to avoid GUI opening
        pass

if __name__ == '__main__':
    unittest.main()
