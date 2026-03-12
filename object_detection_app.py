# Required dependencies:
# pip install opencv-python ultralytics pillow

import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import time
from ultralytics import YOLO
import threading

class CameraSelectionWindow:
    def __init__(self, root, on_camera_selected):
        self.root = root
        self.root.title("Camera Selection")
        self.root.geometry("1200x700")
        self.on_camera_selected = on_camera_selected
        
        # Camera variables
        self.available_cameras = []
        self.camera_caps = {}
        self.selected_cam1 = None
        self.selected_cam2 = None
        self.camera_checkboxes = {}  # Store checkbox references
        self.preview_threads = {}
        self.preview_active = True
        
        # Setup GUI
        self.setup_gui()
        
        # Scan for cameras
        self.scan_cameras()
    
    def setup_gui(self):
        """Set up the camera selection GUI"""
        # Title
        title_label = ttk.Label(self.root, text="Select Two Cameras", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(self.root, text="Select at least one camera for Cam 1 and one for Cam 2 (can be the same camera)")
        instructions.pack(pady=5)
        
        # Camera previews frame
        self.previews_frame = ttk.Frame(self.root)
        self.previews_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Continue button
        self.continue_button = ttk.Button(
            buttons_frame,
            text="Continue",
            command=self.continue_to_app,
            state=tk.DISABLED
        )
        self.continue_button.pack(side=tk.RIGHT, padx=5)
        
        # Refresh button
        refresh_button = ttk.Button(
            buttons_frame,
            text="Refresh",
            command=self.refresh_cameras
        )
        refresh_button.pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Scanning for cameras...")
        self.status_label.pack(pady=5)
        
        # Configure window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def scan_cameras(self):
        """Scan for available cameras"""
        self.status_label.config(text="Scanning for cameras...")
        self.available_cameras = []
        
        # Check cameras 0-4
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.available_cameras.append(i)
                self.camera_caps[i] = cap
                print(f"Found camera {i}")
            else:
                cap.release()
        
        if self.available_cameras:
            self.status_label.config(text=f"Found {len(self.available_cameras)} camera(s)")
            self.create_camera_previews()
        else:
            self.status_label.config(text="No cameras found")
    
    def create_camera_previews(self):
        """Create preview widgets for available cameras"""
        # Clear existing previews
        for widget in self.previews_frame.winfo_children():
            widget.destroy()
        
        # Create grid of camera previews
        cols = min(3, len(self.available_cameras))
        rows = (len(self.available_cameras) + cols - 1) // cols
        
        for idx, camera_idx in enumerate(self.available_cameras):
            row = idx // cols
            col = idx % cols
            
            # Create frame for this camera
            camera_frame = ttk.LabelFrame(
                self.previews_frame,
                text=f"Camera {camera_idx}",
                padding="5"
            )
            camera_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Create label for video preview
            preview_label = ttk.Label(camera_frame)
            preview_label.pack()
            
            # Store reference
            preview_label.camera_idx = camera_idx
            
            # Create checkbox frame
            checkbox_frame = ttk.Frame(camera_frame)
            checkbox_frame.pack(pady=5)
            
            # Create checkboxes for Cam 1 and Cam 2
            cam1_var = tk.BooleanVar()
            cam2_var = tk.BooleanVar()
            
            cam1_checkbox = ttk.Checkbutton(
                checkbox_frame,
                text="Cam 1",
                variable=cam1_var,
                command=lambda idx=camera_idx: self.on_camera_check(idx, 1)
            )
            cam1_checkbox.pack(side=tk.LEFT, padx=5)
            
            cam2_checkbox = ttk.Checkbutton(
                checkbox_frame,
                text="Cam 2",
                variable=cam2_var,
                command=lambda idx=camera_idx: self.on_camera_check(idx, 2)
            )
            cam2_checkbox.pack(side=tk.LEFT, padx=5)
            
            # Store checkbox references
            self.camera_checkboxes[camera_idx] = {
                'cam1_var': cam1_var,
                'cam2_var': cam2_var,
                'cam1_checkbox': cam1_checkbox,
                'cam2_checkbox': cam2_checkbox
            }
            
            # Start preview thread
            self.start_preview_thread(camera_idx, preview_label)
        
        # Configure grid weights
        for i in range(cols):
            self.previews_frame.columnconfigure(i, weight=1)
        for i in range(rows):
            self.previews_frame.rowconfigure(i, weight=1)
    
    def start_preview_thread(self, camera_idx, preview_label):
        """Start a thread to update camera preview"""
        def update_preview():
            cap = self.camera_caps[camera_idx]
            while self.preview_active and cap.isOpened():
                try:
                    # Check if label still exists
                    if not preview_label.winfo_exists():
                        break
                        
                    ret, frame = cap.read()
                    if ret:
                        # Resize frame for preview
                        frame = cv2.resize(frame, (240, 180))
                        
                        # Convert to RGB
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        
                        # Convert to PIL Image
                        image = Image.fromarray(frame_rgb)
                        
                        # Convert to PhotoImage
                        photo = ImageTk.PhotoImage(image=image)
                        
                        # Update label in main thread
                        preview_label.configure(image=photo)
                        preview_label.image = photo  # Keep a reference
                    
                    time.sleep(0.03)  # ~30 FPS
                except Exception as e:
                    # Ignore errors when window is closing
                    if self.preview_active:
                        print(f"Preview error for camera {camera_idx}: {e}")
                    break
        
        thread = threading.Thread(target=update_preview, daemon=True)
        thread.start()
        self.preview_threads[camera_idx] = thread
    
    def on_camera_check(self, camera_idx, cam_num):
        """Handle camera checkbox selection"""
        if cam_num == 1:
            # If this camera is already selected as Cam 2, uncheck it there first
            if self.selected_cam2 == camera_idx:
                self.camera_checkboxes[camera_idx]['cam2_var'].set(False)
                self.selected_cam2 = None
            
            # Update Cam 1 selection
            if self.selected_cam1 is not None and self.selected_cam1 != camera_idx:
                self.camera_checkboxes[self.selected_cam1]['cam1_var'].set(False)
            
            if self.camera_checkboxes[camera_idx]['cam1_var'].get():
                self.selected_cam1 = camera_idx
            else:
                self.selected_cam1 = None
        else:  # cam_num == 2
            # If this camera is already selected as Cam 1, uncheck it there first
            if self.selected_cam1 == camera_idx:
                self.camera_checkboxes[camera_idx]['cam1_var'].set(False)
                self.selected_cam1 = None
            
            # Update Cam 2 selection
            if self.selected_cam2 is not None and self.selected_cam2 != camera_idx:
                self.camera_checkboxes[self.selected_cam2]['cam2_var'].set(False)
            
            if self.camera_checkboxes[camera_idx]['cam2_var'].get():
                self.selected_cam2 = camera_idx
            else:
                self.selected_cam2 = None
        
        # Update status and continue button
        self.update_selection_status()
    
    def update_selection_status(self):
        """Update status label and continue button based on selection"""
        if self.selected_cam1 is not None and self.selected_cam2 is not None:
            self.continue_button.config(state=tk.NORMAL)
            if self.selected_cam1 == self.selected_cam2:
                self.status_label.config(text=f"Selected: Cam 1 & Cam 2 = Camera {self.selected_cam1}")
            else:
                self.status_label.config(text=f"Selected: Cam 1 = Camera {self.selected_cam1}, Cam 2 = Camera {self.selected_cam2}")
        elif self.selected_cam1 is not None:
            self.status_label.config(text=f"Selected: Cam 1 = Camera {self.selected_cam1}, Cam 2 = None")
            self.continue_button.config(state=tk.DISABLED)
        elif self.selected_cam2 is not None:
            self.status_label.config(text=f"Selected: Cam 1 = None, Cam 2 = Camera {self.selected_cam2}")
            self.continue_button.config(state=tk.DISABLED)
        else:
            self.status_label.config(text="Please select at least one camera for Cam 1 and Cam 2")
            self.continue_button.config(state=tk.DISABLED)
    
    def refresh_cameras(self):
        """Refresh camera list"""
        # Stop existing previews
        self.preview_active = False
        time.sleep(0.1)  # Give threads time to stop
        
        # Release all cameras
        for cap in self.camera_caps.values():
            cap.release()
        self.camera_caps = {}
        
        # Reset
        self.selected_cam1 = None
        self.selected_cam2 = None
        self.camera_checkboxes = {}
        self.continue_button.config(state=tk.DISABLED)
        self.preview_active = True
        
        # Rescan
        self.scan_cameras()
    
    def continue_to_app(self):
        """Continue to main application with selected cameras"""
        if self.selected_cam1 is not None and self.selected_cam2 is not None:
            # Stop previews
            self.preview_active = False
            
            # Wait a moment for threads to stop
            time.sleep(0.2)
            
            # Store selected camera captures
            cam1_cap = self.camera_caps[self.selected_cam1]
            cam2_cap = self.camera_caps[self.selected_cam2] if self.selected_cam2 != self.selected_cam1 else None
            
            # If using the same camera for both, we'll need to create a second capture
            if self.selected_cam1 == self.selected_cam2:
                cam2_cap = cv2.VideoCapture(self.selected_cam1)
                if not cam2_cap.isOpened():
                    print("Warning: Could not create second capture for same camera")
                    cam2_cap = cam1_cap  # Fallback to using the same capture
            
            # Clear camera references to prevent thread access
            self.camera_caps = {}
            
            # Call callback with selected cameras
            self.on_camera_selected(self.selected_cam1, self.selected_cam2, cam1_cap, cam2_cap)
            
            # Don't destroy window here - let the callback handle it
            self.root.quit()  # Exit mainloop instead of destroying
    
    def on_closing(self):
        """Handle window closing"""
        self.preview_active = False
        
        # Wait a moment for threads to stop
        time.sleep(0.2)
        
        # Release all cameras
        for cap in self.camera_caps.values():
            cap.release()
        
        self.root.destroy()
        exit(0)

class ObjectDetectionApp:
    def on_closing(self):
        """Handle window closing"""
        if self.cap1 is not None:
            self.cap1.release()
        if self.cap2 is not None:
            self.cap2.release()
        cv2.destroyAllWindows()
        self.root.destroy()
    
    def __init__(self, root, cam1_index=None, cam2_index=None, cam1_cap=None, cam2_cap=None):
        self.root = root
        self.root.title("Dual Camera Object Detection with YOLOv8")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Video capture variables
        self.cap1 = cam1_cap if cam1_cap is not None else None
        self.cap2 = cam2_cap if cam2_cap is not None else None
        self.current_frame1 = None
        self.current_frame2 = None
        self.last_detection_frame1 = None
        self.last_detection_frame2 = None
        self.detection_results1 = None
        self.detection_results2 = None
        self.cam1_index = cam1_index if cam1_index is not None else 0  # Default camera index
        self.cam2_index = cam2_index if cam2_index is not None else 0  # Default camera index
        
        # Timing variables
        self.last_detection_time_cam1 = 0  # Separate timers for each camera
        self.last_detection_time_cam2 = 0
        self.detection_interval = 5  # seconds
        self.video_update_interval = 50  # milliseconds
        
        # Detection state
        self.detection_active = False
        self.model_loaded = False
        self.camera1_active = False
        self.camera2_active = False
        
        # Red dot marker class selection
        self.selected_marker_class = tk.StringVar(value="person")
        self.marker_classes = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
            "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
            "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
            "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
            "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
            "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
            "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
            "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        ]
        
        # Coordinate mapping variables
        self.camera1_type = tk.StringVar(value="top")  # "top" or "front"
        self.camera2_type = tk.StringVar(value="front")
        self.camera1_distance = tk.DoubleVar(value=3.0)  # meters (top camera to floor)
        self.camera2_distance = tk.DoubleVar(value=2.0)  # meters (front camera to room)
        self.room_width = tk.DoubleVar(value=6.0)  # meters
        self.room_length = tk.DoubleVar(value=8.0)  # meters
        self.room_height = tk.DoubleVar(value=3.0)  # meters
        
        # Real-time coordinate storage
        self.current_coordinates = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.last_coordinate_time = None
        self.on_coords_callback = None  # Callback for external coordinate consumers (e.g., ROS 2)
        
        # Initialize GUI
        self.setup_gui()
        
        # Initialize cameras if not provided
        if self.cap1 is None:
            self.initialize_camera1()
        else:
            self.camera1_active = True
            print(f"Using provided camera capture for Camera 1")
            
        if self.cap2 is None:
            self.initialize_camera2()
        else:
            self.camera2_active = True
            print(f"Using provided camera capture for Camera 2")
        
        # Update status
        if self.camera1_active and self.camera2_active:
            self.update_status("Both Cameras Ready", "green")
        elif self.camera1_active:
            self.update_status(f"Camera {self.cam1_index} Ready", "green")
        elif self.camera2_active:
            self.update_status(f"Camera {self.cam2_index} Ready", "green")
        else:
            self.update_status("Camera Error", "red")
        
        # Load YOLO model
        self.load_model()
        
        # Start video loop
        self.update_video()
    
    def setup_gui(self):
        """Set up the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display frame for Camera 1
        video_frame1 = ttk.LabelFrame(main_frame, text=f"Camera {self.cam1_index}", padding="5")
        video_frame1.grid(row=0, column=0, pady=5, padx=5)
        video_frame1.grid_propagate(False)  # Prevent frame from resizing based on content
        video_frame1.configure(width=460, height=350)  # Fixed size
        
        # Video label for displaying frames from Camera 1
        self.video_label1 = ttk.Label(video_frame1)
        self.video_label1.grid(row=0, column=0)
        
        # Video display frame for Camera 2
        video_frame2 = ttk.LabelFrame(main_frame, text=f"Camera {self.cam2_index}", padding="5")
        video_frame2.grid(row=0, column=1, pady=5, padx=5)
        video_frame2.grid_propagate(False)  # Prevent frame from resizing based on content
        video_frame2.configure(width=460, height=350)  # Fixed size
        
        # Video label for displaying frames from Camera 2
        self.video_label2 = ttk.Label(video_frame2)
        self.video_label2.grid(row=0, column=0)
        
        # Control panel frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Start/Stop detection button
        self.detection_button = ttk.Button(
            control_frame,
            text="Start Detection",
            command=self.toggle_detection
        )
        self.detection_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Detection interval controls
        interval_frame = ttk.Frame(control_frame)
        interval_frame.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(interval_frame, text="Interval:").grid(row=0, column=0, padx=2)
        
        # Decrease interval button
        self.decrease_interval_btn = ttk.Button(
            interval_frame,
            text="-",
            width=3,
            command=self.decrease_interval
        )
        self.decrease_interval_btn.grid(row=0, column=1, padx=2)
        
        # Interval display label
        self.interval_label = ttk.Label(interval_frame, text=f"{self.detection_interval:.1f}s")
        self.interval_label.grid(row=0, column=2, padx=5)
        
        # Increase interval button
        self.increase_interval_btn = ttk.Button(
            interval_frame,
            text="+",
            width=3,
            command=self.increase_interval
        )
        self.increase_interval_btn.grid(row=0, column=3, padx=2)
        
        # Red dot marker class selection dropdown
        marker_frame = ttk.Frame(control_frame)
        marker_frame.grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(marker_frame, text="Red Dot Marker:").grid(row=0, column=0, padx=5)
        self.marker_dropdown = ttk.Combobox(
            marker_frame,
            textvariable=self.selected_marker_class,
            values=self.marker_classes,
            state="readonly",
            width=10
        )
        self.marker_dropdown.grid(row=0, column=1, padx=5)
        
        # Status indicator
        status_frame = ttk.Frame(control_frame)
        status_frame.grid(row=0, column=3, padx=20, pady=5)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=5)
        self.status_label = ttk.Label(status_frame, text="Cameras Ready", foreground="green")
        self.status_label.grid(row=0, column=1, padx=5)
        
        # Coordinate mapping control panel
        coordinate_frame = ttk.LabelFrame(main_frame, text="Coordinate Mapping", padding="5")
        coordinate_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Camera 1 settings
        cam1_settings_frame = ttk.Frame(coordinate_frame)
        cam1_settings_frame.grid(row=0, column=0, padx=10, pady=5)
        
        ttk.Label(cam1_settings_frame, text="Camera 1:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(cam1_settings_frame, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.cam1_type_dropdown = ttk.Combobox(
            cam1_settings_frame,
            textvariable=self.camera1_type,
            values=["top", "front"],
            state="readonly",
            width=8
        )
        self.cam1_type_dropdown.grid(row=1, column=1, padx=2)
        
        ttk.Label(cam1_settings_frame, text="Dist to floor/room (m):").grid(row=2, column=0, sticky=tk.W, padx=2)
        self.cam1_distance_entry = ttk.Entry(cam1_settings_frame, textvariable=self.camera1_distance, width=8)
        self.cam1_distance_entry.grid(row=2, column=1, padx=2)
        
        # Camera 2 settings
        cam2_settings_frame = ttk.Frame(coordinate_frame)
        cam2_settings_frame.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(cam2_settings_frame, text="Camera 2:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(cam2_settings_frame, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.cam2_type_dropdown = ttk.Combobox(
            cam2_settings_frame,
            textvariable=self.camera2_type,
            values=["top", "front"],
            state="readonly",
            width=8
        )
        self.cam2_type_dropdown.grid(row=1, column=1, padx=2)
        
        ttk.Label(cam2_settings_frame, text="Dist to floor/room (m):").grid(row=2, column=0, sticky=tk.W, padx=2)
        self.cam2_distance_entry = ttk.Entry(cam2_settings_frame, textvariable=self.camera2_distance, width=8)
        self.cam2_distance_entry.grid(row=2, column=1, padx=2)
        
        # Room dimensions
        room_frame = ttk.Frame(coordinate_frame)
        room_frame.grid(row=0, column=2, padx=10, pady=5)
        
        ttk.Label(room_frame, text="Room Dimensions:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W)
        
        ttk.Label(room_frame, text="Width (X):").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.room_width_entry = ttk.Entry(room_frame, textvariable=self.room_width, width=6)
        self.room_width_entry.grid(row=1, column=1, padx=2)
        
        ttk.Label(room_frame, text="Length (Y):").grid(row=2, column=0, sticky=tk.W, padx=2)
        self.room_length_entry = ttk.Entry(room_frame, textvariable=self.room_length, width=6)
        self.room_length_entry.grid(row=2, column=1, padx=2)
        
        ttk.Label(room_frame, text="Height (Z):").grid(row=3, column=0, sticky=tk.W, padx=2)
        self.room_height_entry = ttk.Entry(room_frame, textvariable=self.room_height, width=6)
        self.room_height_entry.grid(row=3, column=1, padx=2)
        
        # Coordinate display
        coord_display_frame = ttk.Frame(coordinate_frame)
        coord_display_frame.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Label(coord_display_frame, text="Real-time Coordinates:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        
        self.coordinate_label = ttk.Label(
            coord_display_frame,
            text="X: 0.00m  Y: 0.00m  Z: 0.00m",
            font=("Courier", 12, "bold"),
            foreground="blue"
        )
        self.coordinate_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.coord_time_label = ttk.Label(coord_display_frame, text="Last update: --")
        self.coord_time_label.grid(row=2, column=0, columnspan=2)
        
        # Update detection info frame position
        info_frame = ttk.LabelFrame(main_frame, text="Detection Info", padding="5")
        info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Detection count labels
        self.detection_count_label1 = ttk.Label(info_frame, text="Cam 1 Objects: 0")
        self.detection_count_label1.grid(row=0, column=0, padx=5, pady=2)
        
        self.detection_count_label2 = ttk.Label(info_frame, text="Cam 2 Objects: 0")
        self.detection_count_label2.grid(row=0, column=1, padx=5, pady=2)
        
        # Last detection time label
        self.last_detection_label = ttk.Label(info_frame, text="Last detection: Never")
        self.last_detection_label.grid(row=1, column=0, columnspan=2, padx=5, pady=2)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def initialize_camera1(self):
        """Initialize the first webcam"""
        try:
            # Release previous camera if it exists
            if self.cap1 is not None:
                self.cap1.release()
                
            self.cap1 = cv2.VideoCapture(self.cam1_index)
            if not self.cap1.isOpened():
                raise Exception(f"Could not open camera {self.cam1_index}")
            
            # Set camera resolution
            self.cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.camera1_active = True
            print(f"Successfully initialized camera {self.cam1_index}")
        except Exception as e:
            self.update_status(f"Camera 1 Error: {str(e)}", "red")
            print(f"Camera 1 initialization error: {e}")
    
    def initialize_camera2(self):
        """Initialize the second webcam"""
        try:
            # Release previous camera if it exists
            if self.cap2 is not None:
                self.cap2.release()
                
            self.cap2 = cv2.VideoCapture(self.cam2_index)
            if not self.cap2.isOpened():
                raise Exception(f"Could not open camera {self.cam2_index}")
            
            # Set camera resolution
            self.cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.camera2_active = True
            print(f"Successfully initialized camera {self.cam2_index}")
        except Exception as e:
            self.update_status(f"Camera 2 Error: {str(e)}", "red")
            print(f"Camera 2 initialization error: {e}")
    
    def load_model(self):
        """Load the YOLOv8 model"""
        try:
            # Load YOLOv8 model
            self.model = YOLO("yolov8n.pt")
            self.model_loaded = True
            print("YOLOv8 model loaded successfully")
        except Exception as e:
            self.update_status(f"Model Error: {str(e)}", "red")
            print(f"Model loading error: {e}")
    
    def update_video(self):
        """Update video display - runs every 50ms"""
        # Process Camera 1
        if self.camera1_active and self.cap1 is not None:
            try:
                # Read frame from camera 1
                ret, frame = self.cap1.read()
                if ret:
                    self.current_frame1 = frame.copy()
                    
                    # Check if we should run detection
                    current_time = time.time()
                    should_detect = (self.detection_active and
                                    self.model_loaded and
                                    (current_time - self.last_detection_time_cam1 >= self.detection_interval))
                    
                    if should_detect:
                        # Run detection in a separate thread to avoid blocking
                        threading.Thread(target=self.run_detection1, daemon=True).start()
                        self.last_detection_time_cam1 = current_time
                    
                    # Use the last detection results if available
                    display_frame = self.current_frame1.copy()
                    if self.detection_results1 is not None:
                        display_frame = self.draw_detections(display_frame, self.detection_results1, camera_num=1)
                    
                    # Convert frame for Tkinter display
                    self.display_frame1(display_frame)
                    
            except Exception as e:
                print(f"Video update error for Camera 1: {e}")
        
        # Process Camera 2
        if self.camera2_active and self.cap2 is not None:
            try:
                # Read frame from camera 2
                ret, frame = self.cap2.read()
                if ret:
                    self.current_frame2 = frame.copy()
                    
                    # Check if we should run detection for camera 2
                    current_time = time.time()
                    should_detect = (self.detection_active and
                                    self.model_loaded and
                                    (current_time - self.last_detection_time_cam2 >= self.detection_interval))
                    
                    if should_detect:
                        # Run detection in a separate thread to avoid blocking
                        threading.Thread(target=self.run_detection2, daemon=True).start()
                    
                    # Use the last detection results if available
                    display_frame = self.current_frame2.copy()
                    if self.detection_results2 is not None:
                        display_frame = self.draw_detections(display_frame, self.detection_results2, camera_num=2)
                    
                    # Convert frame for Tkinter display
                    self.display_frame2(display_frame)
                    
            except Exception as e:
                print(f"Video update error for Camera 2: {e}")
        
        # Schedule next update
        self.root.after(self.video_update_interval, self.update_video)
    
    def run_detection1(self):
        """Run YOLOv8 detection on camera 1 frame"""
        if self.current_frame1 is not None and self.model_loaded:
            try:
                # Run detection
                results = self.model(self.current_frame1, verbose=False)
                
                # Store results
                self.detection_results1 = results
                self.last_detection_frame1 = self.current_frame1.copy()
                self.last_detection_time_cam1 = time.time()  # Update camera 1's timer
                
                # Update detection info
                self.update_detection_info1(results)
                
            except Exception as e:
                print(f"Detection error for Camera 1: {e}")
    
    def run_detection2(self):
        """Run YOLOv8 detection on camera 2 frame"""
        if self.current_frame2 is not None and self.model_loaded:
            try:
                # Run detection
                results = self.model(self.current_frame2, verbose=False)
                
                # Store results
                self.detection_results2 = results
                self.last_detection_frame2 = self.current_frame2.copy()
                self.last_detection_time_cam2 = time.time()  # Update camera 2's timer
                
                # Update detection info
                self.update_detection_info2(results)
                
            except Exception as e:
                print(f"Detection error for Camera 2: {e}")
    
    def draw_detections(self, frame, results, camera_num=1):
        """Draw bounding boxes and labels on frame
        
        Args:
            frame: The frame to draw on
            results: YOLO detection results
            camera_num: 1 for camera 1, 2 for camera 2
        """
        if results is None or len(results) == 0:
            return frame
        
        # Get the first result
        result = results[0]
        
        # Draw bounding boxes
        for box in result.boxes:
            # Get box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Get confidence and class
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = self.model.names[cls]
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{class_name}: {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw label background
            cv2.rectangle(
                frame,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                (0, 255, 0),
                -1
            )
            
            # Draw label text
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2
            )
            
            # Add red dot to center of selected object type and calculate coordinates
            if class_name == self.selected_marker_class.get():
                # Calculate center of the bounding box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Draw red filled circle at center
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                
                # Calculate world coordinates
                world_coords = self.pixel_to_world_coordinates(center_x, center_y, camera_num)
                
                # Update current coordinates
                if camera_num == 1:
                    # Top camera provides X and Y
                    self.current_coordinates["x"] = world_coords["x"]
                    self.current_coordinates["y"] = world_coords["y"]
                else:
                    # Front camera provides Z
                    self.current_coordinates["z"] = world_coords["z"]
                
                # Update timestamp
                self.last_coordinate_time = time.time()
                
                # Trigger callback if registered (e.g., for ROS 2 publishing)
                if self.on_coords_callback is not None:
                    try:
                        self.on_coords_callback(
                            self.current_coordinates["x"],
                            self.current_coordinates["y"],
                            self.current_coordinates["z"]
                        )
                    except Exception as e:
                        print(f"Error in coordinate callback: {e}")
                
                # Update coordinate display
                self.update_coordinate_display()
        
        return frame
    
    def display_frame1(self, frame):
        """Convert and display frame from Camera 1 in Tkinter"""
        try:
            # Resize frame to 70% of original size (30% smaller)
            height, width = frame.shape[:2]
            new_width = int(width * 0.7)
            new_height = int(height * 0.7)
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert color space from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            image = Image.fromarray(frame_rgb)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image=image)
            
            # Update label
            self.video_label1.configure(image=photo)
            self.video_label1.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Frame display error for Camera 1: {e}")
    
    def display_frame2(self, frame):
        """Convert and display frame from Camera 2 in Tkinter"""
        try:
            # Resize frame to 70% of original size (30% smaller)
            height, width = frame.shape[:2]
            new_width = int(width * 0.7)
            new_height = int(height * 0.7)
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert color space from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            image = Image.fromarray(frame_rgb)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image=image)
            
            # Update label
            self.video_label2.configure(image=photo)
            self.video_label2.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Frame display error for Camera 2: {e}")
    
    def toggle_detection(self):
        """Toggle detection on/off"""
        if not self.model_loaded:
            self.update_status("Model not loaded", "red")
            return
        
        self.detection_active = not self.detection_active
        
        if self.detection_active:
            self.detection_button.configure(text="Stop Detection")
            self.update_status("Detection Active", "green")
            self.last_detection_time_cam1 = 0  # Reset timer to trigger immediate detection
            self.last_detection_time_cam2 = 0  # Reset timer to trigger immediate detection
            
            # Start detection threads for both cameras
            if self.camera1_active:
                threading.Thread(target=self.run_detection1, daemon=True).start()
            if self.camera2_active:
                threading.Thread(target=self.run_detection2, daemon=True).start()
        else:
            self.detection_button.configure(text="Start Detection")
            self.update_status("Detection Stopped", "orange")
    
    def increase_interval(self):
        """Increase detection interval by 0.5 seconds"""
        self.detection_interval += 0.5
        self.interval_label.config(text=f"{self.detection_interval:.1f}s")
        print(f"Detection interval increased to {self.detection_interval:.1f} seconds")
    
    def decrease_interval(self):
        """Decrease detection interval by 0.5 seconds"""
        # Minimum interval of 0.5 seconds to avoid excessive CPU usage
        if self.detection_interval > 0.5:
            self.detection_interval -= 0.5
            self.interval_label.config(text=f"{self.detection_interval:.1f}s")
            print(f"Detection interval decreased to {self.detection_interval:.1f} seconds")
    
    def update_status(self, message, color):
        """Update status label"""
        self.status_label.configure(text=message, foreground=color)
    
    def update_detection_info1(self, results):
        """Update detection information labels for Camera 1"""
        if results is None or len(results) == 0:
            self.detection_count_label1.configure(text="Cam 1 Objects: 0")
            return
        
        # Count detected objects
        result = results[0]
        if result.boxes is not None:
            count = len(result.boxes)
            self.detection_count_label1.configure(text=f"Cam 1 Objects: {count}")
        else:
            self.detection_count_label1.configure(text="Cam 1 Objects: 0")
        
        # Update last detection time
        current_time = time.strftime("%H:%M:%S")
        self.last_detection_label.configure(text=f"Last detection: {current_time}")
    
    def update_detection_info2(self, results):
        """Update detection information labels for Camera 2"""
        if results is None or len(results) == 0:
            self.detection_count_label2.configure(text="Cam 2 Objects: 0")
            return
        
        # Count detected objects
        result = results[0]
        if result.boxes is not None:
            count = len(result.boxes)
            self.detection_count_label2.configure(text=f"Cam 2 Objects: {count}")
        else:
            self.detection_count_label2.configure(text="Cam 2 Objects: 0")
        
        # Update last detection time
        current_time = time.strftime("%H:%M:%S")
        self.last_detection_label.configure(text=f"Last detection: {current_time}")
    
    def pixel_to_world_coordinates(self, pixel_x, pixel_y, camera_num):
        """
        Convert pixel coordinates to real-world 3D coordinates
        
        Args:
            pixel_x: X-coordinate in image (pixels)
            pixel_y: Y-coordinate in image (pixels)
            camera_num: 1 for camera 1, 2 for camera 2
        
        Returns:
            Dictionary with x, y, z coordinates in meters
        """
        # Get camera resolution
        if camera_num == 1:
            image_width = self.cap1.get(cv2.CAP_PROP_FRAME_WIDTH)
            image_height = self.cap1.get(cv2.CAP_PROP_FRAME_HEIGHT)
            camera_type = self.camera1_type.get()
        else:
            image_width = self.cap2.get(cv2.CAP_PROP_FRAME_WIDTH)
            image_height = self.cap2.get(cv2.CAP_PROP_FRAME_HEIGHT)
            camera_type = self.camera2_type.get()
        
        if camera_type == "top":
            # Calculate X and Y from top camera (ceiling view)
            # Normalize pixel coordinates to range [-1, 1]
            normalized_x = (pixel_x - image_width / 2) / (image_width / 2)
            normalized_y = (pixel_y - image_height / 2) / (image_height / 2)
            
            # Convert to world coordinates (meters)
            world_x = normalized_x * (self.room_width.get() / 2)
            world_y = normalized_y * (self.room_length.get() / 2)
            world_z = 0.0  # Will be updated by front camera
            
            return {"x": world_x, "y": world_y, "z": world_z}
        else:
            # Calculate Z from front camera (elevation/height)
            # Normalize pixel coordinates to range [-1, 1]
            normalized_z = (pixel_y - image_height / 2) / (image_height / 2)
            
            # Convert to world coordinates (meters)
            # Assuming camera is centered vertically in the room
            world_z = normalized_z * (self.room_height.get() / 2)
            
            # Ensure Z is positive (above floor)
            world_z = max(0, world_z)
            
            return {"x": 0.0, "y": 0.0, "z": world_z}
    
    def update_coordinate_display(self):
        """Update the coordinate display labels"""
        coords = self.current_coordinates
        
        # Format coordinates to 2 decimal places
        coord_text = f"X: {coords['x']:.2f}m  Y: {coords['y']:.2f}m  Z: {coords['z']:.2f}m"
        self.coordinate_label.config(text=coord_text)
        
        # Update last update time
        if self.last_coordinate_time:
            time_str = time.strftime("%H:%M:%S", time.localtime(self.last_coordinate_time))
            self.coord_time_label.config(text=f"Last update: {time_str}")


def main():
    """Main function to run the application"""
    # Create camera selection window
    root = tk.Tk()
    
    def on_camera_selected(cam1_index, cam2_index, cam1_cap, cam2_cap):
        # Destroy the selection window
        root.destroy()
        
        # Create main application window
        app_root = tk.Tk()
        app = ObjectDetectionApp(app_root, cam1_index, cam2_index, cam1_cap, cam2_cap)
        
        # Set window size and make it resizable
        app_root.geometry("1200x700")
        app_root.minsize(800, 600)
        
        # Run the application
        app_root.mainloop()
    
    # Create camera selection window
    selection_window = CameraSelectionWindow(root, on_camera_selected)
    root.mainloop()

if __name__ == "__main__":
    main()