import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Maximum number of refreshes
        self.max_refreshes = int(os.getenv('MAX_REFRESHES', '100'))
        
        # Image detection settings
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.8'))
        self.item_templates = [
            'assets/templates/item1.png',
            'assets/templates/item2.png'
        ]
        
        # Mouse positions (to be configured)
        self.purchase_button_pos = (0, 0)  # Update with actual coordinates
        self.confirm_button_pos = (0, 0)   # Update with actual coordinates
        self.refresh_button_pos = (0, 0)   # Update with actual coordinates
        self.confirm_refresh_pos = (0, 0)  # Update with actual coordinates
        
        # Timing settings
        self.refresh_delay = float(os.getenv('REFRESH_DELAY', '2.0'))
        self.click_delay = float(os.getenv('CLICK_DELAY', '0.5')) 