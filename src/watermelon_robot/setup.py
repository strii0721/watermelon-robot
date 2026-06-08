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
        
        (os.path.join("share", package_name, "launch"), 
            glob("launch/*.launch.py")),
        
        (os.path.join("share", package_name, "config"), 
            glob("config/*.yaml")),
        
        (os.path.join("share", package_name, "resource", "model-weights", "target-detection"), 
            glob("resource/model-weights/target-detection/*")), 
        
        (os.path.join("share", package_name, "resource", "model-weights", "lane-detection"), 
            glob("resource/model-weights/lane-detection/*")), 
        
        (os.path.join("share", package_name, "templates"), 
            glob("src/watermelon_robot/templates/*.html")), 
        
        (os.path.join("share", package_name, "static", "css"), 
            glob("src/watermelon_robot/static/css/*.css")), 
        
        (os.path.join("share", package_name, "static", "js"), 
            glob("src/watermelon_robot/static/js/*.js")), 
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
            "logic_controller = watermelon_robot.nodes.logic_controller:main",
            "realsense_controller = watermelon_robot.nodes.realsense_controller:main",
            "target_detector = watermelon_robot.nodes.target_detector:main",
            "lane_detector = watermelon_robot.nodes.lane_detector:main",
            "robotic_arm_controller = watermelon_robot.nodes.robotic_arm_controller:main", 
            "chassis_controller = watermelon_robot.nodes.chassis_controller:main",
            "web_app = watermelon_robot.nodes.web_app:main",
            "sub_test = watermelon_robot.nodes.sub_test:main",
        ],
    },
)
