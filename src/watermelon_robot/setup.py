from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'watermelon_robot'

setup(
    name=package_name,
    version='0.0.0',
    package_dir = {"":"./src"},
    packages=find_packages(where = "./src"),
    data_files=[
        ('share/ament_index/resource_index/packages', 
            ['resource/' + package_name]),

        ('share/' + package_name, 
            ['package.xml']),
            
        (os.path.join('share', package_name, 'model_weights'), 
            glob("resource/model_weights/*.pt")), 
        (os.path.join('share', package_name, 'launch'), 
            glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), 
            glob('config/*.yaml'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lynchpin',
    maintainer_email='strii0721@outlook.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            "robotic_arm_controller = controller.robotic_arm_controller:main", 
            "realsense_controller = controller.realsense_controller:main",
            "monitor = tools.monitor:main",
            "centre_controller = controller.centre_controller:main"
        ],
    },
)
