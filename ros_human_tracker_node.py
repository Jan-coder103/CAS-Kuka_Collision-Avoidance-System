#!/usr/bin/env python3
"""
ROS 2 Node Wrapper for Human Tracker

This module provides a ROS 2 node that wraps the existing ObjectDetectionApp
and publishes human position coordinates to a ROS topic.

Author: Generated for CameraObjectDetectionYolo project
ROS 2 Compatibility: Humble / Foxy
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import threading
import sys
import os

# Add parent directory to path to import the original app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from object_detection_app import ObjectDetectionApp, CameraSelectionWindow
except ImportError:
    print("Error: Could not import object_detection_app.py")
    print("Make sure object_detection_app.py is in the same directory")
    sys.exit(1)


class RosHumanTrackerNode(Node):
    """
    ROS 2 Node that publishes human position coordinates.
    
    This node wraps the existing ObjectDetectionApp and publishes
    3D coordinates (x, y, z) to the /human/position_3d topic.
    """
    
    def __init__(self, tracker_instance=None):
        """
        Initialize the ROS 2 node.
        
        Args:
            tracker_instance: Optional ObjectDetectionApp instance to wrap.
                             If None, the node will be attached later.
        """
        super().__init__('human_tracker_node')
        
        # Create publisher for 3D position
        self.publisher_ = self.create_publisher(
            Point,
            '/human/position_3d',
            10  # Queue size
        )
        
        # Store reference to tracker instance
        self.tracker = tracker_instance
        
        # Statistics
        self.publish_count = 0
        self.last_publish_time = None
        
        # Attach callback if tracker instance is provided
        if self.tracker is not None:
            self.attach_to_tracker()
        
        self.get_logger().info('RosHumanTrackerNode initialized')
        self.get_logger().info('Publishing to topic: /human/position_3d')
    
    def attach_to_tracker(self, tracker_instance=None):
        """
        Attach this node to a tracker instance.
        
        Args:
            tracker_instance: ObjectDetectionApp instance to attach to.
                            If None, uses self.tracker.
        """
        if tracker_instance is not None:
            self.tracker = tracker_instance
        
        if self.tracker is not None:
            # Set the callback in the tracker
            self.tracker.on_coords_callback = self.publish_coordinates
            self.get_logger().info('Successfully attached to tracker instance')
        else:
            self.get_logger().warning('No tracker instance to attach to')
    
    def publish_coordinates(self, x, y, z):
        """
        Publish coordinates to the ROS topic.
        
        This method is called by the tracker whenever new coordinates
        are calculated.
        
        Args:
            x: X coordinate in meters
            y: Y coordinate in meters
            z: Z coordinate in meters
        """
        try:
            # Create message
            msg = Point()
            msg.x = float(x)
            msg.y = float(y)
            msg.z = float(z)
            
            # Publish message
            self.publisher_.publish(msg)
            
            # Update statistics
            self.publish_count += 1
            self.last_publish_time = self.get_clock().now()
            
            # Log every 10th publish to avoid spam
            if self.publish_count % 10 == 0:
                self.get_logger().info(
                    f'Published coordinates: x={x:.2f}m, y={y:.2f}m, z={z:.2f}m '
                    f'(Total: {self.publish_count})'
                )
            
        except Exception as e:
            self.get_logger().error(f'Error publishing coordinates: {e}')
    
    def get_statistics(self):
        """
        Get publishing statistics.
        
        Returns:
            Dictionary with publish statistics.
        """
        return {
            'publish_count': self.publish_count,
            'last_publish_time': self.last_publish_time
        }


def run_ros_node(node):
    """
    Run the ROS node in a separate thread.
    
    This function is designed to be run in a daemon thread.
    It spins the ROS node until interrupted.
    
    Args:
        node: RosHumanTrackerNode instance to spin.
    """
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        node.destroy_node()


def main():
    """
    Main entry point for running the tracker with ROS 2.
    
    This function:
    1. Initializes ROS 2
    2. Creates the camera selection window
    3. Creates the ROS node
    4. Starts ROS in a background thread
    5. Runs the GUI mainloop (blocking)
    6. Handles cleanup on exit
    """
    import tkinter as tk
    
    # Initialize ROS 2
    rclpy.init(args=sys.argv)
    
    # Create ROS node (will be attached after tracker is created)
    ros_node = RosHumanTrackerNode()
    
    # Start ROS node in a daemon thread
    # Daemon thread will be killed when main thread exits
    ros_thread = threading.Thread(
        target=run_ros_node,
        args=(ros_node,),
        daemon=True
    )
    ros_thread.start()
    print("ROS 2 node started in background thread")
    
    # Create camera selection window
    root = tk.Tk()
    
    def on_camera_selected(cam1_index, cam2_index, cam1_cap, cam2_cap):
        """
        Callback when cameras are selected.
        
        This function:
        1. Destroys the selection window
        2. Creates the main application
        3. Attaches ROS node to the tracker
        4. Runs the GUI mainloop
        """
        # Destroy the selection window
        root.destroy()
        
        # Create main application window
        app_root = tk.Tk()
        app = ObjectDetectionApp(app_root, cam1_index, cam2_index, cam1_cap, cam2_cap)
        
        # Attach ROS node to the tracker
        ros_node.attach_to_tracker(app)
        print("ROS node attached to tracker")
        
        # Set window size and make it resizable
        app_root.geometry("1200x700")
        app_root.minsize(800, 600)
        
        # Handle window close
        def on_closing():
            """Handle application closing"""
            print("\nShutting down...")
            
            # Print statistics
            stats = ros_node.get_statistics()
            print(f"Total coordinates published: {stats['publish_count']}")
            
            # Destroy ROS node
            rclpy.shutdown()
            
            # Destroy window
            app_root.destroy()
        
        app_root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run the application (blocking)
        app_root.mainloop()
    
    # Create camera selection window
    selection_window = CameraSelectionWindow(root, on_camera_selected)
    
    # Handle window close for selection window
    def on_selection_closing():
        """Handle selection window closing"""
        print("Shutting down ROS 2...")
        rclpy.shutdown()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_selection_closing)
    
    # Run the selection window (blocking)
    root.mainloop()
    
    # Cleanup
    print("Application exited")


if __name__ == "__main__":
    main()
