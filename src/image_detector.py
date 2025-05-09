import cv2
import numpy as np
import pyautogui
from config import Config

class ImageDetector:
    def __init__(self):
        self.config = Config()
        
    def detect_items(self, screenshot=None, debug=False):
        # Take screenshot of the game window or use provided screenshot
        if screenshot is None:
            screenshot = pyautogui.screenshot()
        screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        detected_items = []
        debug_img = screenshot_bgr.copy()
        for template_path in self.config.item_templates:
            template = cv2.imread(template_path)
            if template is None:
                print(f"Warning: Could not load template image: {template_path}")
                continue
            result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val > 0.5:
                print(f"[DEBUG] {template_path} confidence: {max_val}")
            if max_val >= self.config.confidence_threshold:
                item_x, item_y = max_loc
                print(f"Found item at {template_path} at position ({item_x}, {item_y}) with confidence {max_val}")
                detected_items.append((item_x, item_y, template.shape[1], template.shape[0], template_path, max_val))
                # Draw rectangle for debug
                cv2.rectangle(debug_img, (item_x, item_y), (item_x + template.shape[1], item_y + template.shape[0]), (0,255,0), 2)
        if debug and len(detected_items) > 0:
            cv2.imwrite('debug_detection_result.png', debug_img)
            print("[DEBUG] Saved debug_detection_result.png with rectangles on detected items.")
        return detected_items 