import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Maximum number of refreshes
        self.max_refreshes = 100
        
        # Image detection settings
        self.confidence_threshold = 0.97
        self.item_templates = [
            'assets/templates/cov.jpg',
            'assets/templates/mys.jpg',
            'assets/templates/fb.jpg'
        ]
        
        # Mouse positions (to be configured)
        self.purchase_button_pos = (0, 0)  # Update with actual coordinates
        self.confirm_button_pos = (0, 0)   # Update with actual coordinates
        self.refresh_button_pos = (0, 0)   # Update with actual coordinates
        self.confirm_refresh_pos = (0, 0)  # Update with actual coordinates
        
        # Timing settings
        self.refresh_delay = 1.0
        self.click_delay = 0.5

    def create_gui(self):
        image_names = ['cov.jpg', 'mys.jpg', 'fb.jpg']
        image_labels = ['Covenant', 'Mystic', 'Friendship']