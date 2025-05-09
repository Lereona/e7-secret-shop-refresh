# Epic 7 Secret Shop Refresher

This is a Python application to automate secret shop refreshes in the game Epic 7. It uses image detection and mouse control to find and purchase specific items in the shop, with robust buy button matching and a modern, user-friendly GUI.

## Features
- **Robust item detection**: Only detects and purchases items you select in the GUI.
- **Buy button image matching**: Always clicks the correct Buy button for the detected item row using template matching (no manual offsets needed).
- **Per-item purchase counters**: See how many times each item has been purchased.
- **Skystone usage counter**: Tracks and displays total Skystones spent (3 per refresh).
- **Fast, adjustable scrolling**: Scrolls quickly and reliably through the shop.
- **Window and region selection**: Only interacts with your selected game window, with optional region selection.
- **Force Test Mode**: Logs every step and saves screenshots for debugging.
- **Modern GUI**: Easy setup for all positions, region, and item selection, with clear status and error messages.

## Requirements
- Python 3.8+
- Windows OS
- See `requirements.txt` for required Python packages

## Setup
1. Clone this repository or download the source code.
2. Place your item images (`cov.jpg`, `mys.jpg`, `fb.jpg`) and your icon image (`icon.jpg`) in the `assets/templates/` directory.
3. **Place a tightly cropped image of the Buy button as `buy.jpg` in `assets/templates/`.**
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the program:
   ```bash
   python src/main.py
   ```

## How to Use
1. **Configure Settings:**
   - Set the number of max refreshes, confidence threshold, and delays in the Configuration section.
   - Use the "Get Position" buttons to record the mouse positions for each button in the shop (move your mouse and press Enter).
   - Use "Get Buy Offset" to automatically set the vertical offset between the item icon and the Buy button (or just rely on buy button image matching).
2. **Select Items:**
   - Check the boxes for the items you want the bot to look for and purchase. Only selected items will be detected and purchased.
   - The item selection list shows both the item name and the filename for clarity.
3. **Window/Region Selection:**
   - Select your game window from the dropdown at the top.
   - Optionally, set a detection region by clicking the top-left and bottom-right corners in the window.
4. **Start/Stop Automation:**
   - Click the **Start** button or press **Shift** to begin automation.
   - Click the **Stop** button or press **Escape** to stop the automation.
   - You can start and stop the process as many times as you like without closing the program.
5. **Status and Counters:**
   - The status box will show logs and actions as the bot runs. You can scroll through the output.
   - Per-item purchase counters and a Skystones used counter are displayed in the GUI.

## Keyboard Shortcuts
- **Shift**: Start the refresher process
- **Escape**: Stop the refresher process (does not close the window)

## Notes
- Make sure your game window is visible and not obstructed by other windows.
- The bot uses your mouse and screen, so do not use your computer for other tasks while it is running.
- For best results, use item images and buy button images cropped directly from your game client.
- Use "Force Test Mode" for detailed logging and debugging.

## Troubleshooting
- If images do not appear in the GUI, check that they are named correctly and placed in `assets/templates/`.
- If you get errors about mouse positions, ensure you have set them using the "Get Position" buttons.
- If you encounter other issues, check the status box for error messages and use the debug screenshots.

## License
MIT 