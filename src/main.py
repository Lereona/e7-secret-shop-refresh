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
        self.load_item_images()
        
        self.create_gui()
        
    def load_item_images(self):
        print("Loading item images...")
        image_names = ['cov.jpg', 'mys.jpg', 'fb.jpg']
        
        for image_name in image_names:
            image_path = f'assets/templates/{image_name}'
            print(f"Attempting to load: {image_path}")
            
            if os.path.exists(image_path):
                try:
                    # Load and resize image
                    img = Image.open(image_path)
                    # Calculate new size maintaining aspect ratio
                    width, height = img.size
                    max_size = 100  # Smaller size for the image
                    ratio = min(max_size/width, max_size/height)
                    new_size = (int(width*ratio), int(height*ratio))
                    
                    # Resize image
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Store the photo
                    self.item_photos.append(photo)
                    print(f"Successfully loaded image: {image_path}")
                except Exception as e:
                    print(f"Error loading image {image_path}: {e}")
                    self.item_photos.append(None)
            else:
                print(f"Image not found: {image_path}")
                self.item_photos.append(None)
                
    def create_gui(self):
        # Create a canvas and a vertical scrollbar for the main content
        canvas = tk.Canvas(self.root, borderwidth=0, background="#f0f0f0")
        vscrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscrollbar.set)
        vscrollbar.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
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
                
                # Add checkbox
                ttk.Checkbutton(item_container, text="Select", variable=var).pack(pady=5)
                
                # Add purchase counter
                counter_label = ttk.Label(item_container, text=f"Purchased: 0")
                counter_label.pack(pady=5)
                self.counter_labels.append(counter_label)
            else:
                # If no image, just show the checkbox
                ttk.Checkbutton(item_container, text=f"Item {i+1}", variable=var).pack()
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
        
        # Control Buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=row_offset + 4, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_refresher)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_refresher, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Bind Escape key to stop refresher, and Shift to start refresher
        self.root.bind('<Escape>', self.handle_escape)
        self.root.bind('<Shift_L>', self.handle_shift)
        self.root.bind('<Shift_R>', self.handle_shift)
        
    def get_position(self, button_type):
        self.status_text.insert(tk.END, f"Move mouse to {button_type} position and press Enter...\n")
        self.root.update()
        
        def on_enter(event):
            pos = pyautogui.position()
            if button_type == "purchase":
                self.purchase_pos_var.set(str(pos))
            elif button_type == "confirm":
                self.confirm_pos_var.set(str(pos))
            elif button_type == "refresh":
                self.refresh_pos_var.set(str(pos))
            elif button_type == "confirm_refresh":
                self.confirm_refresh_pos_var.set(str(pos))
            self.status_text.insert(tk.END, f"Position set to {pos}\n")
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
                self.config.item_templates.append(f'assets/templates/{["cov.jpg", "mys.jpg", "fb.jpg"][i]}')
        
    def update_purchase_counter(self, item_index):
        """Update the purchase counter for a specific item"""
        if 0 <= item_index < len(self.purchase_counters):
            self.purchase_counters[item_index] += 1
            if self.counter_labels[item_index]:
                self.counter_labels[item_index].config(text=f"Purchased: {self.purchase_counters[item_index]}")
                
    def refresh_loop(self):
        while self.is_running and self.refresh_count < self.config.max_refreshes:
            try:
                # Scroll to bottom of shop
                self.status_text.insert(tk.END, "Scrolling to bottom of shop...\n")
                self.mouse.scroll_to_bottom()
                
                # Check if we're at the bottom
                if self.mouse.is_at_bottom():
                    self.status_text.insert(tk.END, "Reached bottom of shop, scanning for items...\n")
                    
                    # Check for items
                    items_found = self.detector.detect_items()
                    
                    if items_found:
                        self.status_text.insert(tk.END, "Items found! Attempting to purchase...\n")
                        self.mouse.purchase_items()
                        
                        # Update purchase counter for the found item
                        # Note: You'll need to modify the detector to return which item was found
                        # For now, we'll update all selected items
                        for i, var in enumerate(self.item_vars):
                            if var.get():
                                self.update_purchase_counter(i)
                    
                    # Refresh shop
                    self.status_text.insert(tk.END, f"Refreshing shop... (Refresh {self.refresh_count + 1}/{self.config.max_refreshes})\n")
                    self.mouse.refresh_shop()
                    self.refresh_count += 1
                    
                    # Wait for refresh animation
                    time.sleep(self.config.refresh_delay)
                else:
                    self.status_text.insert(tk.END, "Not at bottom yet, continuing to scroll...\n")
                    time.sleep(0.5)  # Small delay before next scroll attempt
                
            except Exception as e:
                self.status_text.insert(tk.END, f"Error occurred: {str(e)}\n")
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

    def handle_escape(self, event=None):
        self.stop_refresher()

    def handle_shift(self, event=None):
        self.start_refresher()

if __name__ == "__main__":
    root = tk.Tk()
    app = SecretShopRefresherGUI(root)
    root.mainloop() 