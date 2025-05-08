# Epic 7 Secret Shop Refresher

This is a Python application to automate secret shop refreshes in the game Epic 7. It uses image detection and mouse control to find and purchase specific items in the shop.

## Features
- GUI for easy configuration
- Select which items to detect and purchase
- Set mouse positions for shop buttons
- Start/stop automation with buttons or keyboard shortcuts
- Scrollable interface for easy navigation
- Profile icon at the top for fun customization

## Requirements
- Python 3.8+
- Windows OS
- See `requirements.txt` for required Python packages

## Setup
1. Clone this repository or download the source code.
2. Place your item images (`cov.jpg`, `mys.jpg`, `fb.jpg`) and your icon image (`icon.jpg`) in the `assets/templates/` directory.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the program:
   ```bash
   python src/main.py
   ```

## How to Use
1. **Configure Settings:**
   - Set the number of max refreshes, confidence threshold, and delays in the Configuration section.
   - Use the "Get Position" buttons to record the mouse positions for each button in the shop (move your mouse and press Enter).
2. **Select Items:**
   - Check the boxes for the items you want the bot to look for and purchase.
3. **Start/Stop Automation:**
   - Click the **Start** button or press **Shift** to begin automation.
   - Click the **Stop** button or press **Escape** to stop the automation.
   - You can start and stop the process as many times as you like without closing the program.
4. **Status:**
   - The status box will show logs and actions as the bot runs. You can scroll through the output.

## Keyboard Shortcuts
- **Shift**: Start the refresher process
- **Escape**: Stop the refresher process (does not close the window)

## Notes
- Make sure your game window is visible and not obstructed by other windows.
- The bot uses your mouse and screen, so do not use your computer for other tasks while it is running.
- For best results, use item images cropped directly from your game client.

## Troubleshooting
- If images do not appear in the GUI, check that they are named correctly and placed in `assets/templates/`.
- If you get errors about mouse positions, ensure you have set them using the "Get Position" buttons.
- If you encounter other issues, check the status box for error messages.

## License
MIT 