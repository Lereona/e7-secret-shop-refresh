import time
import pyautogui
from image_detector import ImageDetector
from mouse_controller import MouseController
from config import Config

class SecretShopRefresher:
    def __init__(self):
        self.config = Config()
        self.detector = ImageDetector()
        self.mouse = MouseController()
        self.refresh_count = 0
        
    def run(self):
        print("Starting Secret Shop Refresher...")
        print(f"Maximum refreshes set to: {self.config.max_refreshes}")
        
        while self.refresh_count < self.config.max_refreshes:
            try:
                # Check for items
                items_found = self.detector.detect_items()
                
                if items_found:
                    print("Items found! Attempting to purchase...")
                    self.mouse.purchase_items()
                
                # Refresh shop
                print(f"Refreshing shop... (Refresh {self.refresh_count + 1}/{self.config.max_refreshes})")
                self.mouse.refresh_shop()
                self.refresh_count += 1
                
                # Wait for refresh animation
                time.sleep(self.config.refresh_delay)
                
            except Exception as e:
                print(f"Error occurred: {str(e)}")
                break
                
        print("Finished running Secret Shop Refresher")

if __name__ == "__main__":
    refresher = SecretShopRefresher()
    refresher.run() 