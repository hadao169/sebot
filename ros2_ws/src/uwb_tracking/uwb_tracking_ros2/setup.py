from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'uwb_tracking_ros2'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    py_modules=[
        'uwb_tracking_ros2.dwm1001_apiCommands'
    ],
    # Files we want to install, specifically launch files
    data_files=[
        # Install marker file in the package index        
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),              
        # (os.path.join('share', package_name, 'resource'), glob('resource/*')),          
        # Include our package.xml file
        (os.path.join('share', package_name), ['package.xml']),
        # Include all launch files.
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml'))),
        (os.path.join('share', package_name, 'msg'), glob(os.path.join('msg', '*.msg'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author='Lauritz Keysberg, Cung Lian Sang',
    author_email='lkeysberg@techfak.uni-bielefeld.de, csang@techfak.uni-bielefeld.de',
    maintainer='ROS 2 Developer',
    maintainer_email='ros2@ros.com',
    description='UWB Tracking in ROS2.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'uwb_tracking_dwm1001 = uwb_tracking_ros2.uwb_tracking_dwm1001:main',
            'viz_dwm1001 = uwb_tracking_ros2.viz_dwm1001:main',
        ],
    },
)