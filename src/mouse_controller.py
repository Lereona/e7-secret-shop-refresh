import pyautogui
import time
import cv2
import numpy as np
from config import Config

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
            drag_distance = 350  # pixels to drag up (lowered)
            steps = 10  # faster scroll
            print(f"[DEBUG] Scrolling with drag_distance={drag_distance}, steps={steps}")
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            time.sleep(0.05)
            for i in range(steps):
                current_y = start_y - (drag_distance * (i + 1) / steps)
                pyautogui.moveTo(start_x, current_y, duration=0.005)
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
            # Load the Buy button template
            buy_template = cv2.imread('assets/templates/buy.jpg')
            if buy_template is None:
                print("[ERROR] Could not load buy button template at assets/templates/buy.jpg")
                return
            # Take a screenshot of the window
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
                # Click confirm button (still use configured position)
                if click_func:
                    click_func(*self.config.confirm_button_pos)
                else:
                    pyautogui.click(self.config.confirm_button_pos)
                time.sleep(self.config.click_delay)
                print("Successfully purchased item at detected position")
            else:
                print("[WARN] Buy button not found near detected item. No click performed.")
        except Exception as e:
            print(f"Error during purchase at detected position: {str(e)}") 