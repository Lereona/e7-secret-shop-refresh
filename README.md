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

5. Update mouse positions in `src/config.py` with the correct coordinates for your screen

## Usage

Run the script:
```bash
python src/main.py
```

## Features

- Automated shop refreshing
- Image detection for specific items
- Configurable refresh count
- Automatic purchasing of detected items
- Error handling and logging

## Notes

- Make sure the game window is visible and not minimized
- The script uses image detection, so it's important to have clear template images
- Adjust the confidence threshold if needed for better detection 