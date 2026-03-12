# Minimal Changes to object_detection_app.py for ROS 2 Integration

This document shows the exact changes needed to add ROS 2 callback support to the original script.

## Change 1: Add callback attribute in `__init__` method

**Location**: Line 386 (after `self.last_coordinate_time = None`)

**Add this line**:
```python
self.on_coords_callback = None  # Callback for external coordinate consumers (e.g., ROS 2)
```

**Context**:
```python
        # Real-time coordinate storage
        self.current_coordinates = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.last_coordinate_time = None
        self.on_coords_callback = None  # Callback for external coordinate consumers (e.g., ROS 2)
```

## Change 2: Trigger callback in `draw_detections` method

**Location**: Line 836 (after `self.last_coordinate_time = time.time()`)

**Add this code**:
```python
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
```

**Context**:
```python
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
```

## Summary

**Total changes**: 2 additions, 0 deletions, 0 modifications
**Lines added**: ~10 lines
**Impact**: Zero - these changes are backward compatible and don't affect existing functionality

## How to Apply

You can apply these changes manually or use the following diff:

```diff
diff --git a/object_detection_app.py b/object_detection_app.py
index original..modified 100644
--- a/object_detection_app.py
+++ b/object_detection_app.py
@@ -383,6 +383,7 @@ class ObjectDetectionApp:
         # Real-time coordinate storage
         self.current_coordinates = {"x": 0.0, "y": 0.0, "z": 0.0}
         self.last_coordinate_time = None
+        self.on_coords_callback = None  # Callback for external coordinate consumers (e.g., ROS 2)
         
         # Initialize GUI
         self.setup_gui()
@@ -833,6 +834,15 @@ class ObjectDetectionApp:
                 # Update timestamp
                 self.last_coordinate_time = time.time()
                 
+                # Trigger callback if registered (e.g., for ROS 2 publishing)
+                if self.on_coords_callback is not None:
+                    try:
+                        self.on_coords_callback(
+                            self.current_coordinates["x"],
+                            self.current_coordinates["y"],
+                            self.current_coordinates["z"]
+                        )
+                    except Exception as e:
+                        print(f"Error in coordinate callback: {e}")
+                
                 # Update coordinate display
                 self.update_coordinate_display()
```

## Verification

After applying changes, verify:

1. Run the original script without ROS 2:
   ```bash
   python object_detection_app.py
   ```
   - Should work exactly as before
   - GUI should display normally
   - No errors related to callback

2. The callback mechanism is now available for ROS 2 wrapper to use
