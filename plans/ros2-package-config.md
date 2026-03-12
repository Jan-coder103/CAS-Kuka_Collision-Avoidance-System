# ROS 2 Package Configuration Files

This document contains the ROS 2 package configuration files needed to create a proper ROS 2 package.

## File 1: package.xml

**File**: `package.xml`

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>human_tracker</name>
  <version>1.0.0</version>
  <description>ROS 2 wrapper for dual camera human tracking with YOLO object detection</description>
  <maintainer email="user@example.com">Your Name</maintainer>
  <license>MIT</license>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

## File 2: setup.py

**File**: `setup.py`

```python
from setuptools import setup

package_name = 'human_tracker'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='user@example.com',
    description='ROS 2 wrapper for dual camera human tracking with YOLO object detection',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'human_tracker_node = human_tracker.ros_human_tracker_node:main',
        ],
    },
)
```

## File 3: setup.cfg

**File**: `setup.cfg`

```ini
[develop]
script-dir=$base/lib/human_tracker
[install]
install-scripts=$base/lib/human_tracker
```

## File 4: requirements.txt

**File**: `requirements.txt`

```txt
# ROS 2 dependencies
rclpy>=5.0.0
geometry_msgs

# Vision and ML dependencies
opencv-python>=4.5.0
ultralytics>=8.0.0
pillow>=9.0.0

# GUI dependencies (already in standard library)
# tkinter
```

## File 5: resource/human_tracker

**File**: `resource/human_tracker`

```text
human_tracker
```

## Package Structure

After creating these files, your package structure should look like:

```
human_tracker/                          # ROS 2 workspace package
├── package.xml                         # Package manifest
├── setup.py                            # Python setup configuration
├── setup.cfg                           # Setup configuration
├── resource/
│   └── human_tracker                   # Package marker file
├── requirements.txt                    # Python dependencies
├── human_tracker/                      # Python package directory
│   ├── __init__.py                    # Package initialization
│   └── ros_human_tracker_node.py      # ROS 2 node implementation
└── object_detection_app.py             # Original application (modified)
```

## Installation Steps

### Option 1: As a ROS 2 Package (Recommended)

1. **Create ROS 2 workspace structure**:
   ```bash
   cd ~/ros2_ws/src
   mkdir -p human_tracker
   cd human_tracker
   ```

2. **Copy files to package directory**:
   - Create `human_tracker/` subdirectory
   - Copy `ros_human_tracker_node.py` to `human_tracker/`
   - Create `__init__.py` in `human_tracker/`
   - Copy `object_detection_app.py` to package root
   - Create configuration files (package.xml, setup.py, etc.)

3. **Create `__init__.py`**:
   ```python
   # human_tracker/__init__.py
   ```
   (Empty file is sufficient)

4. **Build the package**:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select human_tracker
   ```

5. **Source the workspace**:
   ```bash
   source ~/ros2_ws/install/setup.bash
   ```

6. **Run the node**:
   ```bash
   ros2 run human_tracker human_tracker_node
   ```

### Option 2: Standalone Script (Simpler)

If you don't want to create a full ROS 2 package, you can run it as a standalone script:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the script**:
   ```bash
   source /opt/ros/humble/setup.bash
   python ros_human_tracker_node.py
   ```

## Verification

After installation, verify the package:

```bash
# Check if package is recognized
ros2 pkg list | grep human_tracker

# Check node
ros2 node list  # Should show /human_tracker_node when running

# Check topic
ros2 topic list | grep human
```

## ROS 2 Compatibility

This package is compatible with:
- ROS 2 Humble Hawksbill (Ubuntu 22.04)
- ROS 2 Foxy Fitzroy (Ubuntu 20.04)

## Dependencies

### System Dependencies
- Python 3.8+
- ROS 2 Humble or Foxy
- OpenCV
- Tkinter (usually included with Python)

### Python Dependencies
See `requirements.txt` above

## Troubleshooting

### Import Errors
If you get import errors, ensure:
1. ROS 2 environment is sourced: `source /opt/ros/humble/setup.bash`
2. All dependencies are installed: `pip install -r requirements.txt`
3. `object_detection_app.py` is in the same directory

### Package Not Found
If `ros2 pkg list` doesn't show the package:
1. Ensure you've built the package: `colcon build`
2. Source the workspace: `source ~/ros2_ws/install/setup.bash`
3. Check package.xml syntax

### Node Not Starting
If the node doesn't start:
1. Check Python version: `python --version` (should be 3.8+)
2. Verify ROS 2 is installed: `ros2 --version`
3. Check for missing dependencies
