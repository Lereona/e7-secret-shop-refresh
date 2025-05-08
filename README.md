# Epic 7 Secret Shop Refresher

An automated tool for refreshing the Secret Shop in Epic 7 using image detection and mouse control.

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the `.env` file with your settings:
   ```
   MAX_REFRESHES=100
   CONFIDENCE_THRESHOLD=0.8
   REFRESH_DELAY=2.0
   CLICK_DELAY=0.5
   ```

4. Add item template images to `assets/templates/`:
   - `item1.png`: Template image for the first item to detect
   - `item2.png`: Template image for the second item to detect

5. Update mouse positions in `src/config.py` with the correct coordinates for your screen:
   ```python
   self.purchase_button_pos = (x, y)  # Replace with actual coordinates
   self.confirm_button_pos = (x, y)   # Replace with actual coordinates
   self.refresh_button_pos = (x, y)   # Replace with actual coordinates
   self.confirm_refresh_pos = (x, y)  # Replace with actual coordinates
   ```

## Usage

1. Open Epic 7 in Google Play Games beta emulator
2. Navigate to the Secret Shop
3. Run the script:
   ```bash
   python src/main.py
   ```

4. To stop the program, press Ctrl+C

## Features

- Automated shop refreshing
- Image detection for specific items
- Configurable refresh count
- Automatic purchasing of detected items
- Error handling and logging
- Fail-safe mode (move mouse to corner to stop)

## Notes

- Make sure the game window is visible and not minimized
- The script uses image detection, so it's important to have clear template images
- Adjust the confidence threshold if needed for better detection
- The program will automatically stop after reaching the maximum number of refreshes
- You can stop the program at any time by pressing Ctrl+C or moving your mouse to any corner of the screen 