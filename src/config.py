import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Maximum number of refreshes
        self.max_refreshes = 100
        
        # Image detection settings
        self.confidence_threshold = 0.8
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
        self.refresh_delay = 2.0
        self.click_delay = 0.5 