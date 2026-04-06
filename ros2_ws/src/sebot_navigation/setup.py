from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'sebot_navigation'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='k5001682',
    maintainer_email='ha6bnnt@gmail.com',
    description='Navigation package for Sebot',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'uwb_goal_publisher = sebot_navigation.publish:main',
            'waypoint_publisher = sebot_navigation.waypoint_follower:main',
        ],
    },
)