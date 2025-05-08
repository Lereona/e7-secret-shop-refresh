import cv2
import numpy as np
import pyautogui
from config import Config

class ImageDetector:
    def __init__(self):
        self.config = Config()
        
    def detect_items(self):
        # Take screenshot of the game window
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        items_found = False
        
        # Check for each item template
        for template_path in self.config.item_templates:
            template = cv2.imread(template_path)
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            locations = np.where(result >= self.config.confidence_threshold)
            
            if len(locations[0]) > 0:
                items_found = True
                break
                
        return items_found 