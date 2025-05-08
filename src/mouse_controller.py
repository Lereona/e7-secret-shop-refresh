import pyautogui
import time
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
            
    def scroll_to_bottom(self):
        try:
            # Get the current mouse position
            start_x, start_y = pyautogui.position()
            
            # Calculate the drag distance (adjust these values based on your screen)
            drag_distance = 500  # pixels to drag down
            
            # Perform the drag operation
            pyautogui.moveTo(start_x, start_y)
            pyautogui.mouseDown()
            time.sleep(0.1)  # Small delay before dragging
            
            # Smooth drag down
            steps = 20  # Number of steps for smooth movement
            for i in range(steps):
                current_y = start_y + (drag_distance * (i + 1) / steps)
                pyautogui.moveTo(start_x, current_y, duration=0.01)
            
            pyautogui.mouseUp()
            time.sleep(self.config.click_delay)
            print("Scrolled to bottom of shop")
            
            # Return mouse to original position
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