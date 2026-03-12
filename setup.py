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
