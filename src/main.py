import time
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import pyautogui
from PIL import Image, ImageTk
import os
from image_detector import ImageDetector
from mouse_controller import MouseController
from config import Config
import re
import keyboard  # Add this import at the top
import pygetwindow as gw  # Add this import at the top
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SecretShopRefresherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Epic 7 Secret Shop Refresher")
        self.root.geometry("1000x1000")  # Increased window size
        
        # Prepare stretched profile picture (cropped center square, then stretched)
        self.profile_photo = None
        try:
            icon_path = 'assets/templates/icon.jpg'
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                width, height = icon_img.size
                min_dim = min(width, height)
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                icon_img = icon_img.crop((left, top, right, bottom))
                # Stretch to a much wider, short rectangle for a goofier effect
                icon_img = icon_img.resize((512, 64), Image.Resampling.LANCZOS)
                self.profile_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, self.profile_photo)
        except Exception as e:
            print(f"Error loading/cropping icon: {e}")
        
        self.config = Config()
        self.detector = ImageDetector()
        self.mouse = MouseController()
        self.refresh_count = 0
        self.is_running = False
        self.refresh_thread = None
        
        # Initialize purchase counters
        self.purchase_counters = [0, 0, 0]
        
        # Store references to images
        self.item_photos = []  # Store PhotoImage objects
        self.item_labels = []  # Store Label widgets
        
        # Load item images
        self.image_names = ['cov.jpg', 'mys.jpg', 'fb.jpg']
        self.image_labels = ['Covenant', 'Mystic', 'Friendship']
        self.load_item_images()
        
        self.selected_window = None
        self.window_offset = (0, 0)
        self.window_size = (0, 0)
        self.window_list = []
        self.selected_region = [0, 0, 0, 0]  # x, y, w, h relative to window
        self.region_set = False
        self.create_window_selector()
        self.create_region_selector()
        
        self.force_test_mode = tk.BooleanVar(value=False)
        self.buy_button_offset_y = 0
        
        self.skystone_count = 0
        
        self.create_gui()
        
        self.global_hotkey_thread = threading.Thread(target=self.listen_for_escape, daemon=True)
        self.global_hotkey_thread.start()
        
    def load_item_images(self):
        print("Loading item images...")
        for image_name in self.image_names:
            image_path = resource_path(f'assets/templates/{image_name}')
            print(f"Attempting to load: {image_path}")
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path)
                    width, height = img.size
                    max_size = 100
                    ratio = min(max_size/width, max_size/height)
                    new_size = (int(width*ratio), int(height*ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.item_photos.append(photo)
                    print(f"Successfully loaded image: {image_path}")
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    self.item_photos.append(None)
            else:
                print(f"Image not found: {image_path}")
                self.item_photos.append(None)
                
    def create_window_selector(self):
        # Add a dropdown at the top of the GUI for window selection
        window_frame = ttk.Frame(self.root)
        window_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(window_frame, text="Select Game Window:").pack(side=tk.LEFT)
        self.window_var = tk.StringVar()
        self.window_dropdown = ttk.Combobox(window_frame, textvariable=self.window_var, state='readonly')
        self.refresh_window_list()
        self.window_dropdown.pack(side=tk.LEFT, padx=5)
        ttk.Button(window_frame, text="Refresh List", command=self.refresh_window_list).pack(side=tk.LEFT)
        ttk.Button(window_frame, text="Set Window", command=self.set_selected_window).pack(side=tk.LEFT)

    def refresh_window_list(self):
        self.window_list = [w.title for w in gw.getAllWindows() if w.title.strip()]
        self.window_dropdown['values'] = self.window_list
        if self.window_list:
            self.window_var.set(self.window_list[0])

    def set_selected_window(self):
        title = self.window_var.get()
        win = next((w for w in gw.getAllWindows() if w.title == title), None)
        if win:
            self.selected_window = win
            self.window_offset = (win.left, win.top)
            self.window_size = (win.width, win.height)
            self.status_text.insert(tk.END, f"Selected window: {title} at {self.window_offset} size {self.window_size}\n")
        else:
            self.status_text.insert(tk.END, "Window not found!\n")

    def create_region_selector(self):
        # Add region selection controls below window selector
        region_frame = ttk.Frame(self.root)
        region_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(region_frame, text="Detection Region (x, y, w, h):").pack(side=tk.LEFT)
        self.region_vars = [tk.StringVar(value='0') for _ in range(4)]
        for i, label in enumerate(['X', 'Y', 'W', 'H']):
            ttk.Label(region_frame, text=label).pack(side=tk.LEFT)
            ttk.Entry(region_frame, textvariable=self.region_vars[i], width=5).pack(side=tk.LEFT)
        ttk.Button(region_frame, text="Set Region", command=self.set_region).pack(side=tk.LEFT)
        ttk.Button(region_frame, text="Full Window", command=self.set_full_window_region).pack(side=tk.LEFT)
        ttk.Button(region_frame, text="Set Region by Click", command=self.set_region_by_click).pack(side=tk.LEFT)

    def set_region(self):
        try:
            self.selected_region = [int(v.get()) for v in self.region_vars]
            self.region_set = True
            self.status_text.insert(tk.END, f"Detection region set to {self.selected_region}\n")
        except Exception as e:
            self.status_text.insert(tk.END, f"Error setting region: {e}\n")

    def set_full_window_region(self):
        if self.selected_window:
            self.selected_region = [0, 0, self.window_size[0], self.window_size[1]]
            for i, v in enumerate(self.selected_region):
                self.region_vars[i].set(str(v))
            self.region_set = True
            self.status_text.insert(tk.END, f"Detection region set to full window: {self.selected_region}\n")
        else:
            self.status_text.insert(tk.END, "No window selected!\n")

    def set_region_by_click(self):
        if not self.selected_window:
            self.status_text.insert(tk.END, "No window selected!\n")
            return
        self.status_text.insert(tk.END, "Move mouse to TOP-LEFT of region and press Enter...\n")
        self.root.update()
        def on_enter_top_left(event):
            top_left = pyautogui.position()
            self.status_text.insert(tk.END, f"Top-left: {top_left}\nMove mouse to BOTTOM-RIGHT of region and press Enter...\n")
            self.root.unbind('<Return>')
            def on_enter_bottom_right(event):
                bottom_right = pyautogui.position()
                self.status_text.insert(tk.END, f"Bottom-right: {bottom_right}\n")
                win_x, win_y = self.window_offset
                x1, y1 = top_left[0] - win_x, top_left[1] - win_y
                x2, y2 = bottom_right[0] - win_x, bottom_right[1] - win_y
                rx, ry = min(x1, x2), min(y1, y2)
                rw, rh = abs(x2 - x1), abs(y2 - y1)
                self.selected_region = [rx, ry, rw, rh]
                for i, v in enumerate(self.selected_region):
                    self.region_vars[i].set(str(v))
                self.region_set = True
                self.status_text.insert(tk.END, f"Detection region set by click: {self.selected_region}\n")
                self.root.unbind('<Return>')
            self.root.bind('<Return>', on_enter_bottom_right)
        self.root.bind('<Return>', on_enter_top_left)

    def get_window_screenshot(self):
        if self.selected_window:
            x, y = self.window_offset
            w, h = self.window_size
            # Always use the full window for detection
            region = (x, y, w, h)
            screenshot = pyautogui.screenshot(region=region)
            return screenshot
        else:
            return pyautogui.screenshot()

    def region_offset(self):
        # Returns (rx, ry) offset for clicks if region is set
        if self.region_set:
            return self.selected_region[0], self.selected_region[1]
        return 0, 0

    def click_in_window(self, x, y):
        if self.selected_window:
            win_x, win_y = self.window_offset
            rx, ry = self.region_offset()
            screen_x = win_x + rx + x
            screen_y = win_y + ry + y
        else:
            screen_x, screen_y = x, y
        # Validate click is within screen bounds
        screen_w, screen_h = pyautogui.size()
        if 0 <= screen_x < screen_w and 0 <= screen_y < screen_h:
            pyautogui.click(screen_x, screen_y)
        else:
            self.status_text.insert(tk.END, f"Click out of bounds: ({screen_x}, {screen_y})\n")

    def click_in_window_absolute(self, x, y):
        if self.selected_window:
            win_x, win_y = self.window_offset
            screen_x = win_x + x
            screen_y = win_y + y
        else:
            screen_x, screen_y = x, y
        screen_w, screen_h = pyautogui.size()
        if 0 <= screen_x < screen_w and 0 <= screen_y < screen_h:
            pyautogui.click(screen_x, screen_y)
        else:
            self.status_text.insert(tk.END, f"Click out of bounds: ({screen_x}, {screen_y})\n")

    def test_click(self):
        # Test click at purchase button position
        try:
            pos = self.parse_position(self.purchase_pos_var.get())
            self.click_in_window(*pos)
            self.status_text.insert(tk.END, f"Test click at {pos} in window offset.\n")
        except Exception as e:
            self.status_text.insert(tk.END, f"Test click error: {e}\n")

    def test_detection(self):
        try:
            screenshot = self.get_window_screenshot()
            screenshot.save('test_detection_screenshot.png')
            self.status_text.insert(tk.END, "Saved screenshot for detection test as test_detection_screenshot.png\n")
            # Optionally, run detection and show result
            item_info = self.detector.detect_items()
            if item_info:
                self.status_text.insert(tk.END, f"Detection test: Item found at {item_info}\n")
            else:
                self.status_text.insert(tk.END, "Detection test: No item found.\n")
        except Exception as e:
            self.status_text.insert(tk.END, f"Detection test error: {e}\n")

    def create_gui(self):
        image_names = self.image_names
        image_labels = self.image_labels
        # Create a canvas and a vertical scrollbar for the main content
        canvas = tk.Canvas(self.root, borderwidth=0, background="#f0f0f0")
        vscrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)
        # Place main content at row=2
        vscrollbar.grid(row=2, column=1, sticky="ns")
        canvas.grid(row=2, column=0, sticky="nsew")
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a frame inside the canvas to hold all widgets
        main_frame = ttk.Frame(canvas, padding="20")
        self.main_frame = main_frame  # Store reference if needed
        # Add the frame to the canvas
        frame_id = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        # Update scrollregion when the frame size changes
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        main_frame.bind("<Configure>", on_frame_configure)

        # Enable scrolling with mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Add profile picture at the top
        if self.profile_photo:
            profile_label = tk.Label(main_frame, image=self.profile_photo)
            profile_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        row_offset = 1 if self.profile_photo else 0
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=row_offset, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Max Refreshes
        ttk.Label(config_frame, text="Max Refreshes:").grid(row=0, column=0, sticky=tk.W)
        self.max_refreshes_var = tk.StringVar(value=str(self.config.max_refreshes))
        ttk.Entry(config_frame, textvariable=self.max_refreshes_var, width=10).grid(row=0, column=1, sticky=tk.W)
        
        # Confidence Threshold
        ttk.Label(config_frame, text="Confidence Threshold:").grid(row=1, column=0, sticky=tk.W)
        self.confidence_var = tk.StringVar(value=str(self.config.confidence_threshold))
        ttk.Entry(config_frame, textvariable=self.confidence_var, width=10).grid(row=1, column=1, sticky=tk.W)
        
        # Delays
        ttk.Label(config_frame, text="Refresh Delay (s):").grid(row=2, column=0, sticky=tk.W)
        self.refresh_delay_var = tk.StringVar(value=str(self.config.refresh_delay))
        ttk.Entry(config_frame, textvariable=self.refresh_delay_var, width=10).grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(config_frame, text="Click Delay (s):").grid(row=3, column=0, sticky=tk.W)
        self.click_delay_var = tk.StringVar(value=str(self.config.click_delay))
        ttk.Entry(config_frame, textvariable=self.click_delay_var, width=10).grid(row=3, column=1, sticky=tk.W)
        
        # Mouse Positions Section
        mouse_frame = ttk.LabelFrame(main_frame, text="Mouse Positions", padding="10")
        mouse_frame.grid(row=row_offset + 1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Purchase Button Position
        ttk.Label(mouse_frame, text="Purchase Button:").grid(row=0, column=0, sticky=tk.W)
        self.purchase_pos_var = tk.StringVar(value=str(self.config.purchase_button_pos))
        ttk.Entry(mouse_frame, textvariable=self.purchase_pos_var, width=20).grid(row=0, column=1, sticky=tk.W)
        ttk.Button(mouse_frame, text="Get Position", command=lambda: self.get_position("purchase")).grid(row=0, column=2)
        
        # Confirm Purchase Button Position
        ttk.Label(mouse_frame, text="Confirm Purchase:").grid(row=1, column=0, sticky=tk.W)
        self.confirm_pos_var = tk.StringVar(value=str(self.config.confirm_button_pos))
        ttk.Entry(mouse_frame, textvariable=self.confirm_pos_var, width=20).grid(row=1, column=1, sticky=tk.W)
        ttk.Button(mouse_frame, text="Get Position", command=lambda: self.get_position("confirm")).grid(row=1, column=2)
        
        # Refresh Button Position
        ttk.Label(mouse_frame, text="Refresh Button:").grid(row=2, column=0, sticky=tk.W)
        self.refresh_pos_var = tk.StringVar(value=str(self.config.refresh_button_pos))
        ttk.Entry(mouse_frame, textvariable=self.refresh_pos_var, width=20).grid(row=2, column=1, sticky=tk.W)
        ttk.Button(mouse_frame, text="Get Position", command=lambda: self.get_position("refresh")).grid(row=2, column=2)
        
        # Confirm Refresh Position
        ttk.Label(mouse_frame, text="Confirm Refresh:").grid(row=3, column=0, sticky=tk.W)
        self.confirm_refresh_pos_var = tk.StringVar(value=str(self.config.confirm_refresh_pos))
        ttk.Entry(mouse_frame, textvariable=self.confirm_refresh_pos_var, width=20).grid(row=3, column=1, sticky=tk.W)
        ttk.Button(mouse_frame, text="Get Position", command=lambda: self.get_position("confirm_refresh")).grid(row=3, column=2)
        
        # Add Get Buy Offset button
        ttk.Button(mouse_frame, text="Get Buy Offset", command=self.get_buy_offset).grid(row=4, column=2)
        self.buy_offset_var = tk.StringVar(value=str(self.buy_button_offset_y))
        ttk.Label(mouse_frame, text="Buy Offset Y:").grid(row=4, column=0, sticky=tk.W)
        ttk.Entry(mouse_frame, textvariable=self.buy_offset_var, width=10).grid(row=4, column=1, sticky=tk.W)
        
        # Item Selection Section
        item_frame = ttk.LabelFrame(main_frame, text="Item Selection", padding="10")
        item_frame.grid(row=row_offset + 2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.item_vars = []
        self.counter_labels = []
        
        # Create a frame for items
        items_container = ttk.Frame(item_frame)
        items_container.grid(row=0, column=0, pady=10)
        
        for i in range(3):
            var = tk.BooleanVar(value=True)
            self.item_vars.append(var)
            
            # Create a frame for each item
            item_container = ttk.Frame(items_container)
            item_container.grid(row=0, column=i, padx=20, pady=10)
            
            # Add image if available
            if self.item_photos[i]:
                # Create a frame for the image with border
                img_frame = ttk.Frame(item_container, relief="solid", borderwidth=2)
                img_frame.pack(pady=5)
                
                # Create and store the image label
                img_label = ttk.Label(img_frame, image=self.item_photos[i])
                img_label.pack(padx=5, pady=5)
                self.item_labels.append(img_label)
                
                # Add checkbox with filename
                ttk.Checkbutton(item_container, text=f"{image_labels[i]} ({image_names[i]})", variable=var).pack(pady=5)
                
                # Add purchase counter
                counter_label = ttk.Label(item_container, text=f"Purchased: 0")
                counter_label.pack(pady=5)
                self.counter_labels.append(counter_label)
            else:
                # If no image, just show the checkbox with filename
                ttk.Checkbutton(item_container, text=f"Item {i+1} ({image_names[i]})", variable=var).pack()
                self.counter_labels.append(None)
                self.item_labels.append(None)
        
        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=row_offset + 3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Add a vertical scrollbar to the status text area
        self.status_text = tk.Text(status_frame, height=10, width=80, wrap=tk.WORD)
        status_scrollbar = ttk.Scrollbar(status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=status_scrollbar.set)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Add skystone counter display below status section
        self.skystone_var = tk.StringVar(value="Skystones used: 0")
        skystone_label = ttk.Label(self.root, textvariable=self.skystone_var, font=("Arial", 12, "bold"))
        skystone_label.grid(row=4, column=0, sticky='w', padx=10, pady=5)
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=row_offset + 4, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_refresher)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_refresher, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Bind Shift to start refresher
        self.root.bind('<Shift_L>', self.handle_shift)
        self.root.bind('<Shift_R>', self.handle_shift)
        
        # Place test buttons at row=3 (below main content)
        test_frame = ttk.Frame(self.root)
        test_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=5)
        ttk.Button(test_frame, text="Test Click", command=self.test_click).pack(side=tk.LEFT, padx=5)
        ttk.Button(test_frame, text="Test Detection", command=self.test_detection).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(test_frame, text="Force Test Mode (log everything)", variable=self.force_test_mode).pack(side=tk.LEFT, padx=5)
        
    def get_position(self, button_type):
        self.status_text.insert(tk.END, f"Move mouse to {button_type} position and press Enter...\n")
        self.root.update()
        def on_enter(event):
            pos = pyautogui.position()
            if self.selected_window:
                win_x, win_y = self.window_offset
                rel_pos = (pos[0] - win_x, pos[1] - win_y)
            else:
                rel_pos = pos
            if button_type == "purchase":
                self.purchase_pos_var.set(str(rel_pos))
            elif button_type == "confirm":
                self.confirm_pos_var.set(str(rel_pos))
            elif button_type == "refresh":
                self.refresh_pos_var.set(str(rel_pos))
            elif button_type == "confirm_refresh":
                self.confirm_refresh_pos_var.set(str(rel_pos))
            self.status_text.insert(tk.END, f"Position set to {rel_pos}\n")
            self.root.unbind('<Return>')
        self.root.bind('<Return>', on_enter)
        
    def parse_position(self, pos_str):
        # Handles formats like '(x, y)', 'Point(x, y)', and 'Point(x=..., y=...)'
        match = re.search(r'(-?\d+),\s*(-?\d+)', pos_str)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        match = re.search(r'x\s*=\s*(-?\d+)[,)]\s*y\s*=\s*(-?\d+)', pos_str)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        raise ValueError(f'Invalid position string: {pos_str}')
        
    def update_config(self):
        self.config.max_refreshes = int(self.max_refreshes_var.get())
        self.config.confidence_threshold = float(self.confidence_var.get())
        self.config.refresh_delay = float(self.refresh_delay_var.get())
        self.config.click_delay = float(self.click_delay_var.get())
        
        # Update mouse positions
        self.config.purchase_button_pos = self.parse_position(self.purchase_pos_var.get())
        self.config.confirm_button_pos = self.parse_position(self.confirm_pos_var.get())
        self.config.refresh_button_pos = self.parse_position(self.refresh_pos_var.get())
        self.config.confirm_refresh_pos = self.parse_position(self.confirm_refresh_pos_var.get())
        
        # Update item templates based on selection
        self.config.item_templates = []
        for i, var in enumerate(self.item_vars):
            if var.get():
                self.config.item_templates.append(f'assets/templates/{self.image_names[i]}')
        
        try:
            self.buy_button_offset_y = int(self.buy_offset_var.get())
        except Exception:
            self.buy_button_offset_y = 0
        
    def update_purchase_counter(self, item_index):
        """Update the purchase counter for a specific item"""
        if 0 <= item_index < len(self.purchase_counters):
            self.purchase_counters[item_index] += 1
            if self.counter_labels[item_index]:
                self.counter_labels[item_index].config(text=f"Purchased: {self.purchase_counters[item_index]}")
                
    def refresh_loop(self):
        while self.is_running and self.refresh_count < self.config.max_refreshes:
            try:
                purchased_this_refresh = set()
                selected_templates = []
                for i, var in enumerate(self.item_vars):
                    if var.get():
                        selected_templates.append(f'assets/templates/{self.image_names[i]}')
                # 1. Scan for items (before scroll)
                self.status_text.insert(tk.END, "Scanning for items (before scroll)...\n")
                screenshot = self.get_window_screenshot()
                if self.force_test_mode.get():
                    screenshot.save(f'force_test_before_scroll_{self.refresh_count}.png')
                detected_items = self.detector.detect_items(screenshot=screenshot, debug=True, templates=selected_templates)
                for item in detected_items:
                    item_x, item_y, item_w, item_h, template_path, conf = item
                    item_id = (item_x, item_y, template_path)
                    if item_id not in purchased_this_refresh:
                        msg = f"[BEFORE SCROLL] Item at ({item_x}, {item_y}) from {template_path} (conf: {conf:.2f}), purchasing...\n"
                        print(msg.strip())
                        self.status_text.insert(tk.END, msg)
                        self.mouse.purchase_item_at(item_x, item_y, item_w, item_h, click_func=self.click_in_window, buy_button_offset_y=self.buy_button_offset_y)
                        purchased_this_refresh.add(item_id)
                        # Update only the counter for the purchased item
                        for i, var in enumerate(self.item_vars):
                            if var.get() and template_path.endswith(self.image_names[i]):
                                self.update_purchase_counter(i)
                                break
                        break  # Only one purchase per scan phase, then handle confirm
                if not detected_items:
                    self.status_text.insert(tk.END, "No item found before scroll.\n")
                # 2. Scroll
                self.status_text.insert(tk.END, "Scrolling to bottom of shop...\n")
                self.mouse.scroll_to_bottom(window_offset=self.window_offset, window_size=self.window_size)
                # 3. Scan for items (after scroll)
                self.status_text.insert(tk.END, "Scanning for items (after scroll)...\n")
                screenshot = self.get_window_screenshot()
                if self.force_test_mode.get():
                    screenshot.save(f'force_test_after_scroll_{self.refresh_count}.png')
                detected_items = self.detector.detect_items(screenshot=screenshot, debug=True, templates=selected_templates)
                for item in detected_items:
                    item_x, item_y, item_w, item_h, template_path, conf = item
                    item_id = (item_x, item_y, template_path)
                    if item_id not in purchased_this_refresh:
                        msg = f"[AFTER SCROLL] Item at ({item_x}, {item_y}) from {template_path} (conf: {conf:.2f}), purchasing...\n"
                        print(msg.strip())
                        self.status_text.insert(tk.END, msg)
                        self.mouse.purchase_item_at(item_x, item_y, item_w, item_h, click_func=self.click_in_window, buy_button_offset_y=self.buy_button_offset_y)
                        purchased_this_refresh.add(item_id)
                        # Update only the counter for the purchased item
                        for i, var in enumerate(self.item_vars):
                            if var.get() and template_path.endswith(self.image_names[i]):
                                self.update_purchase_counter(i)
                                break
                        break  # Only one purchase per scan phase, then handle confirm
                if not detected_items:
                    self.status_text.insert(tk.END, "No item found after scroll.\n")
                # 4. Refresh shop (use absolute window coords)
                msg = f"Refreshing shop... (Refresh {self.refresh_count + 1}/{self.config.max_refreshes}) at {self.config.refresh_button_pos}\n"
                print(msg.strip())
                self.status_text.insert(tk.END, msg)
                self.click_in_window_absolute(*self.config.refresh_button_pos)
                time.sleep(self.config.click_delay)
                msg = f"Confirming refresh at {self.config.confirm_refresh_pos}\n"
                print(msg.strip())
                self.status_text.insert(tk.END, msg)
                self.click_in_window_absolute(*self.config.confirm_refresh_pos)
                time.sleep(self.config.click_delay)
                self.refresh_count += 1
                # Update skystone counter
                self.skystone_count += 3
                self.skystone_var.set(f"Skystones used: {self.skystone_count}")
                # Wait for refresh animation
                time.sleep(self.config.refresh_delay)
            except Exception as e:
                self.status_text.insert(tk.END, f"Error occurred: {str(e)}\n")
                print(f"[ERROR] {e}")
                break
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_text.insert(tk.END, f"Finished after {self.refresh_count} refreshes\n")
        
    def start_refresher(self):
        self.update_config()
        self.is_running = True
        self.refresh_count = 0
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.refresh_thread = threading.Thread(target=self.refresh_loop)
        self.refresh_thread.start()
        
    def stop_refresher(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_text.insert(tk.END, "Stopping refresher...\n")

    def handle_shift(self, event=None):
        self.start_refresher()

    def listen_for_escape(self):
        while True:
            keyboard.wait('esc')
            self.stop_refresher()

    def get_buy_offset(self):
        self.status_text.insert(tk.END, "Move mouse to CENTER of item icon and press Enter...\n")
        self.root.update()
        def on_enter_item(event):
            item_pos = pyautogui.position()
            self.status_text.insert(tk.END, f"Item icon center: {item_pos}\nMove mouse to CENTER of Buy button in same row and press Enter...\n")
            self.root.unbind('<Return>')
            def on_enter_buy(event):
                buy_pos = pyautogui.position()
                offset_y = buy_pos[1] - item_pos[1]
                self.buy_button_offset_y = offset_y
                self.buy_offset_var.set(str(offset_y))
                self.status_text.insert(tk.END, f"Buy button offset Y set to {offset_y}\n")
                self.root.unbind('<Return>')
            self.root.bind('<Return>', on_enter_buy)
        self.root.bind('<Return>', on_enter_item)

if __name__ == "__main__":
    root = tk.Tk()
    app = SecretShopRefresherGUI(root)
    root.mainloop() 