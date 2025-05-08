import pyautogui
import time
from config import Config

class MouseController:
    def __init__(self):
        self.config = Config()
        
    def purchase_items(self):
        # Click purchase button
        pyautogui.click(self.config.purchase_button_pos)
        time.sleep(self.config.click_delay)
        
        # Click confirm button
        pyautogui.click(self.config.confirm_button_pos)
        time.sleep(self.config.click_delay)
        
    def refresh_shop(self):
        # Click refresh button
        pyautogui.click(self.config.refresh_button_pos)
        time.sleep(self.config.click_delay)
        
        # Click confirm refresh button
        pyautogui.click(self.config.confirm_refresh_pos)
        time.sleep(self.config.click_delay) 