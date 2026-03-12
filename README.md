# Camera Object Detection with YOLOv8 and ROS2 Integration

A comprehensive object detection system that combines real-time dual-camera object detection using YOLOv8 with ROS2 integration for human tracking applications.

## Overview

This project provides two main components:
1. **Standalone GUI Application** - A user-friendly interface for real-time object detection using YOLOv8 on dual camera feeds
2. **ROS2 Human Tracker Node** - A ROS2 package that integrates YOLOv8 object detection for human tracking in robotics applications

The system captures video from webcams, processes frames to detect objects using YOLOv8, and can either display results in a GUI application or publish detection data via ROS2 topics for integration with robotics systems.

## Features

### Standalone GUI Application
- **Dual Camera Support**: Simultaneously captures and displays live video feeds from two webcams
- **Flexible Camera Selection**: Choose which cameras to use as Cam 1 and Cam 2 (can be same camera)
- **YOLOv8 Object Detection**: Utilizes YOLOv8 models (nano/small/medium) for efficient object detection
- **Interactive GUI**: Clean and intuitive interface built with Tkinter
- **Detection Controls**: Start/stop detection with a simple button click
- **Detection Information**: Displays real-time statistics including object count and last detection time
- **Performance Optimized**: Runs detection in separate threads to maintain smooth video playback
- **Visual Feedback**: Draws bounding boxes and labels with confidence scores
- **Person Identification**: Red dots at the center of detected persons for easy identification

### ROS2 Integration
- **ROS2 Package**: Full ROS2 package structure for robotics integration
- **Human Tracking Node**: Specialized node for tracking humans in camera feeds
- **Topic Publishing**: Publishes detection results to ROS2 topics
- **Coordinate Mapping**: Supports coordinate transformation between camera and world frames
- **Multi-Model Support**: Compatible with different YOLOv8 model sizes

## Requirements

### Dependencies

#### For Standalone GUI Application
```bash
pip install opencv-python ultralytics pillow
```

#### For ROS2 Integration
```bash
pip install opencv-python ultralytics pillow
```

Additionally, you need ROS2 installed on your system. This package is compatible with ROS2 Humble, Iron, and Jazzy distributions.

### Hardware

- One or two working webcams (built-in or USB)
- Minimum 4GB RAM recommended
- CPU with decent performance for real-time processing of video streams
- For ROS2: Compatible Linux system with ROS2 installed

## Installation

### Standalone GUI Application

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install opencv-python ultralytics pillow
   ```
3. Run the application:
   ```bash
   python object_detection_app.py
   ```

### ROS2 Package

1. Ensure ROS2 is installed on your system
2. Clone this repository into your ROS2 workspace (e.g., `~/ros2_ws/src/`)
3. Install dependencies:
   ```bash
   cd ~/ros2_ws
   pip install opencv-python ultralytics pillow
   ```
4. Build the package:
   ```bash
   colcon build --packages-select human_tracker
   source install/setup.bash
   ```
5. Run the ROS2 node:
   ```bash
   ros2 run human_tracker ros_human_tracker_node
   ```

## Usage

1. Launch the application by running `object_detection_app.py`
2. **Camera Selection Window**:
   - The application first opens a camera selection window that appears immediately
   - It automatically scans for available cameras (takes 1-2 seconds)
   - Live preview feeds are displayed for all detected cameras
   - Under each camera preview, there are two checkboxes: "Cam 1" and "Cam 2"
   - Select at least one camera for Cam 1 and at least one camera for Cam 2 (can be the same camera)
   - Click "Continue" to proceed with the selected cameras
3. **Main Application**:
   - After camera selection, the main application window opens with two video feeds side by side
   - The YOLOv8 model loads (takes 20-30 seconds on first run, downloads model if needed)
   - Video feeds from both selected cameras appear once model loading completes
4. Click "Start Detection" to begin object detection on both cameras simultaneously
5. Detected objects will appear with green bounding boxes and labels on both feeds
6. Detected persons will have a red dot at their center for easy identification on both cameras
7. Click "Stop Detection" to pause detection while keeping the video feeds active
8. Close the window to exit the application

**Note**: The camera selection window appears immediately with no delay. The 20-30 second delay only occurs after you've selected cameras and the main application is loading the YOLOv8 model.

## GUI Components

### Camera Selection Window
- **Camera Previews**: Live preview feeds from all detected cameras (up to 5)
- **Selection Interface**: Two checkboxes under each camera (Cam 1 and Cam 2)
- **Validation Logic**: Ensures at least one camera is selected for each position
- **Continue Button**: Proceed to the main application with the selected cameras
- **Refresh Button**: Rescan for available cameras

### Main Application - Video Feed
- Displays two live camera feeds side by side with detection overlays
- Shows bounding boxes and labels for detected objects on both feeds
- Red dots at the center of detected persons for easy identification on both cameras

### Main Application - Controls
- **Start/Stop Detection Button**: Toggle object detection on/off for both cameras simultaneously
- **Interval Controls**: Adjust detection frequency with +/- buttons (default: 5.0 seconds, applies to both cameras)
- **Status Indicator**: Shows the current application status (Cameras Ready, Detection Active, etc.)

### Main Application - Detection Info
- **Cam 1 Objects**: Shows the count of objects detected in the last detection frame from Camera 1
- **Cam 2 Objects**: Shows the count of objects detected in the last detection frame from Camera 2
- **Last Detection**: Displays the timestamp of the most recent detection

## Technical Details

### Detection Parameters
- **Models**: YOLOv8 variants available:
  - `yolov8n.pt` - Nano model (fastest, lowest accuracy)
  - `yolov8s.pt` - Small model (balanced)
  - `yolov8m.pt` - Medium model (slower, higher accuracy)
- **Detection Interval**: 5 seconds (adjustable in 0.5 second increments, minimum 0.5 seconds)
- **Video Update Rate**: 50ms (20 FPS display)
- **Camera Resolution**: 640x480 pixels (configurable)

### Performance Considerations
- Detection runs in separate threads to prevent UI freezing
- Detection is performed at intervals rather than every frame to maintain smooth video playback
- The last detection results are displayed on subsequent frames until new detection is performed
- When using the same physical camera for both feeds, a second capture instance is created
- Model selection impacts performance: nano > small > medium (in terms of speed)

### ROS2 Topics
- **Published Topics**:
  - `/human_tracker/detections` - Detection messages with bounding boxes and classes
  - `/human_tracker/coordinates` - Transformed coordinates in world frame
- **Parameters**:
  - `model_path`: Path to YOLOv8 model file (default: `yolov8n.pt`)
  - `camera_index`: Camera device index (default: 0)
  - `detection_interval`: Time between detections in seconds (default: 5.0)

## File Structure

```
CameraObjectDetectionYolo/
├── object_detection_app.py          # Standalone GUI application
├── ros_human_tracker_node.py        # ROS2 human tracker node
├── package.xml                      # ROS2 package manifest
├── setup.py                         # ROS2 package setup
├── setup.cfg                        # ROS2 package configuration
├── requirements.txt                 # Python dependencies
├── human_tracker/                   # ROS2 package directory
│   └── __init__.py
├── plans/                           # Documentation and planning files
│   ├── coordinate-mapping-control-panel.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── object_detection_app_ros2_changes.md
│   ├── README_ROS2.md
│   ├── ros_human_tracker_node.py.md
│   ├── ros2-integration-plan.md
│   └── ros2-package-config.md
├── resource/                        # ROS2 package resources
│   └── human_tracker
├── yolov8n.pt                       # YOLOv8 nano model
├── yolov8s.pt                       # YOLOv8 small model
├── yolov8m.pt                       # YOLOv8 medium model
├── yolov.zip                        # Model archive
└── README.md                        # This documentation file
```

## Troubleshooting

### Common Issues

1. **Camera not found**:
   - Ensure your webcams are connected and not being used by another application
   - Check if the cameras are properly recognized by your system
   - Try refreshing the camera list in the selection window

2. **Model loading errors**:
   - Ensure you have an active internet connection for the first run (model auto-download)
   - Check if you have sufficient disk space for the model file

3. **Performance issues**:
   - Close other applications that might be using the cameras
   - Consider adjusting the detection interval in the code if needed
   - Using two cameras requires more processing power than a single camera

4. **Same camera for both feeds not working**:
   - Some cameras may not support multiple simultaneous captures
   - Try using different physical cameras for Cam 1 and Cam 2

### Error Messages

- "Camera Error: Could not open camera X": The application couldn't access camera with index X
- "Model Error: [error details]": Issues loading the YOLOv8 model
- "Model not loaded": Attempting to start detection before the model is loaded
- "Warning: Could not create second capture for same camera": The selected camera doesn't support multiple simultaneous captures
- If camera selection doesn't work: Ensure your cameras are properly connected and recognized by your system

### Startup Process

When you run the application, the following happens:

**Stage 1: Camera Selection (Immediate)**
1. Camera selection window appears immediately
2. Application scans for available cameras (1-2 seconds)
3. Live preview feeds start for all detected cameras
4. You can select cameras for Cam 1 and Cam 2 positions and click Continue

**Stage 2: Main Application (After Camera Selection)**
1. Main application window opens with two video feed areas
2. Camera initialization completes quickly for both cameras
3. YOLOv8 model loading takes the most time (20-30 seconds):
   - First run: Downloads 6MB model file from Ultralytics servers
   - Subsequent runs: Loads the model from local storage
4. Video feeds start displaying once model loading completes

During startup, you'll see status messages in the terminal like:
```
Found camera 0
Found camera 1
Successfully initialized camera 0
Successfully initialized camera 1
YOLOv8 model loaded successfully
```

## Customization

### Standalone Application Parameters
You can modify the following parameters in `object_detection_app.py`:

- `detection_interval`: Change the time between detections (line 351) - can also be adjusted with +/- buttons in the GUI
- `video_update_interval`: Adjust the video refresh rate (line 352)
- Camera resolution (lines 496-497 and 517-518)
- Model selection (line 530) - you can use other YOLOv8 variants
- Maximum cameras to check (line 82) - Adjust if you have more than 5 cameras
- Preview frame size (line 180) - Adjust the camera preview size in the selection window
- Minimum detection interval (line 725) - Change the lower limit for interval adjustment

### ROS2 Node Parameters
You can configure the ROS2 node using:

1. **Launch file parameters**: Modify parameters in a custom launch file
2. **ROS2 parameters**: Set parameters at runtime:
   ```bash
   ros2 run human_tracker ros_human_tracker_node --ros-args -p model_path:=yolov8s.pt -p detection_interval:=3.0
   ```
3. **YAML configuration file**: Create a parameter file for consistent configuration

## Documentation

Additional documentation is available in the `plans/` directory:
- `README_ROS2.md` - Detailed ROS2 integration guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details and architecture
- `ros2-integration-plan.md` - ROS2 integration planning document
- `coordinate-mapping-control-panel.md` - Coordinate mapping documentation
- `ros_human_tracker_node.py.md` - ROS2 node specific documentation

## License

This project is provided as-is for educational and development purposes. Please respect the licenses of the underlying libraries and models used.

## Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) for the object detection model
- [OpenCV](https://opencv.org/) for computer vision operations
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework
- [ROS2](https://docs.ros.org/en/humble/) for the robotics middleware

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for bug fixes, feature requests, or improvements.

## Future Enhancements

- Support for more YOLOv8 model variants
- Integration with additional ROS2 message types
- Multi-camera tracking with coordinate fusion
- Real-time performance optimization
- Web-based interface for remote monitoring
- Support for depth cameras and 3D tracking