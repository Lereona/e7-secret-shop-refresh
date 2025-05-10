import pyautogui
import time
import cv2
import numpy as np
from config import Config
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MouseController:
    def __init__(self):
        self.config = Config()
        # Set PyAutoGUI to fail-safe mode
        pyautogui.FAILSAFE = True
        
    def purchase_items(self):
        try:
            # Click purchase button
            pyautogui.click(self.config.purchase_button_pos)
            time.sleep(self.config.click_delay)
            
            # Click confirm button
            pyautogui.click(self.config.confirm_button_pos)
            time.sleep(self.config.click_delay)
            print("Successfully purchased items")
        except Exception as e:
            print(f"Error during purchase: {str(e)}")
        
    def refresh_shop(self):
        try:
            # Click refresh button
            pyautogui.click(self.config.refresh_button_pos)
            time.sleep(self.config.click_delay)
            
            # Click confirm refresh button
            pyautogui.click(self.config.confirm_refresh_pos)
            time.sleep(self.config.click_delay)
            print("Successfully refreshed shop")
        except Exception as e:
            print(f"Error during refresh: {str(e)}")
            
    def scroll_to_bottom(self, window_offset=None, window_size=None):
        try:
            # Use the vertical center of the window if available, else current mouse position
            if window_offset and window_size:
                start_x = window_offset[0] + window_size[0] // 2
                start_y = window_offset[1] + window_size[1] // 2
                print(f"Scrolling from window center: ({start_x}, {start_y})")
            else:
                start_x, start_y = pyautogui.position()
                print(f"Scrolling from current mouse position: ({start_x}, {start_y})")
            drag_distance = 400  # increased scroll distance
            steps = 5  # fast scroll
            print(f"[DEBUG] Scrolling with drag_distance={drag_distance}, steps={steps}")
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            time.sleep(0.02)
            for i in range(steps):
                current_y = start_y - (drag_distance * (i + 1) / steps)
                pyautogui.moveTo(start_x, current_y, duration=0.002)
            pyautogui.mouseUp()
            time.sleep(self.config.click_delay)
            print(f"Scrolled to bottom of shop (dragged up {drag_distance} pixels)")
            pyautogui.moveTo(start_x, start_y)
        except Exception as e:
            print(f"Error during scroll: {str(e)}")
            
    def is_at_bottom(self):
        """
        Check if we've reached the bottom of the shop
        Returns True if at bottom, False otherwise
        """
        try:
            # Take a screenshot before and after a small scroll
            before_scroll = pyautogui.screenshot()
            pyautogui.scroll(-100)  # Try to scroll down a bit
            time.sleep(0.1)
            after_scroll = pyautogui.screenshot()
            
            # Compare the screenshots
            # If they're identical, we're at the bottom
            return before_scroll == after_scroll
            
        except Exception as e:
            print(f"Error checking bottom: {str(e)}")
            return False 

    def purchase_item_at(self, item_x, item_y, item_w, item_h, click_func=None, **kwargs):
        try:
            # Always use assets/templates/ for image paths
            buy_template_path = resource_path(os.path.join('assets', 'templates', 'buy.jpg'))
            confirm_buy_template_path = resource_path(os.path.join('assets', 'templates', 'confirmBuy.jpg'))
            buy_template = cv2.imread(buy_template_path)
            if buy_template is None:
                print(f"[ERROR] Could not load buy button template at {buy_template_path}")
                return
            # Take a screenshot of the window (before click)
            screenshot = pyautogui.screenshot()
            screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            # Crop a horizontal strip at the detected item's Y
            strip_margin = 30
            y1 = max(0, item_y - strip_margin)
            y2 = min(screenshot_bgr.shape[0], item_y + item_h + strip_margin)
            strip = screenshot_bgr[y1:y2, :]
            # Match the Buy button in the strip
            result = cv2.matchTemplate(strip, buy_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            print(f"[DEBUG] Buy button match confidence: {max_val}")
            threshold = 0.7  # You can adjust this if needed
            if max_val >= threshold:
                buy_x = max_loc[0] + buy_template.shape[1] // 2
                buy_y = y1 + max_loc[1] + buy_template.shape[0] // 2
                print(f"Clicking Buy button at ({buy_x}, {buy_y})")
                if click_func:
                    click_func(buy_x, buy_y)
                else:
                    pyautogui.click(buy_x, buy_y)
                time.sleep(self.config.click_delay)
                # Take a fresh screenshot and detect confirmBuy button near the center of the screen
                confirm_buy_template = cv2.imread(confirm_buy_template_path)
                if confirm_buy_template is not None:
                    screenshot2 = pyautogui.screenshot()
                    screenshot2_bgr = cv2.cvtColor(np.array(screenshot2), cv2.COLOR_RGB2BGR)
                    h, w, _ = screenshot2_bgr.shape
                    center_y = h // 2
                    region_margin = 100
                    region_y1 = max(0, center_y - region_margin)
                    region_y2 = min(h, center_y + region_margin)
                    region = screenshot2_bgr[region_y1:region_y2, :]
                    result_cb = cv2.matchTemplate(region, confirm_buy_template, cv2.TM_CCOEFF_NORMED)
                    min_val_cb, max_val_cb, min_loc_cb, max_loc_cb = cv2.minMaxLoc(result_cb)
                    print(f"[DEBUG] confirmBuy match confidence: {max_val_cb}")
                    cb_threshold = 0.7
                    if max_val_cb >= cb_threshold:
                        cb_x = max_loc_cb[0] + confirm_buy_template.shape[1] // 2
                        cb_y = region_y1 + max_loc_cb[1] + confirm_buy_template.shape[0] // 2 + 50  # Shift 10 pixels lower
                        print(f"Clicking confirmBuy at ({cb_x}, {cb_y}) (shifted 10px lower)")
                        if click_func:
                            click_func(cb_x, cb_y)
                        else:
                            pyautogui.click(cb_x, cb_y)
                        time.sleep(self.config.click_delay)
                    else:
                        print(f"[WARN] {confirm_buy_template_path} template not found.")
                else:
                    print(f"[WARN] {confirm_buy_template_path} template not found.")
                print("Successfully purchased item at detected position")
            else:
                print("[WARN] Buy button not found near detected item. No click performed.")
        except Exception as e:
            print(f"Error during purchase at detected position: {str(e)}") 