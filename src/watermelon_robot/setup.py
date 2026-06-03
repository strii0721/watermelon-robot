from setuptools import find_packages, setup
from glob import glob
import os

package_name = "watermelon_robot"

setup(
    name=package_name,
    version="0.0.0",
    package_dir = {"":"./src"},
    packages=find_packages(where = "src"),
    data_files=[
        ("share/ament_index/resource_index/packages", 
            ["resource/" + package_name]),
        ("share/" + package_name, 
            ["package.xml"]),
        (os.path.join("share", package_name, "model-weights", "target-detection"), 
            glob("resource/model-weights/target-detection/*")), 
        (os.path.join("share", package_name, "model-weights", "lane-detection"), 
            glob("resource/model-weights/lane-detection/*")), 
        (os.path.join("share", package_name, "launch"), 
            glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), 
            glob("config/*.yaml"))
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="lynchpin",
    maintainer_email="strii0721@outlook.com",
    description="TODO: Package description",
    license="TODO: License declaration",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "super_logic_controller = nodes.super_logic_controller:main", 
            "sub_logic_controller = nodes.sub_logic_controller:main",
            "robotic_arm_controller = nodes.robotic_arm_controller:main", 
            "chassis_controller = nodes.chassis_controller:main",
            "realsense_controller = nodes.realsense_controller:main",
            "monitor = nodes.monitor:main", 
            "lane_detector = nodes.lane_detector:main",
            "target_detector = nodes.target_detector:main",
            "sub_test = nodes.sub_test:main"
        ],
    },
)
