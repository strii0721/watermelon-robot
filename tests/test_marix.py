import numpy as np
from utils.camera_utils import CameraUtils

print(
    CameraUtils._get_marix_wTtcp() @ CameraUtils._get_marix_tcpTc()
)