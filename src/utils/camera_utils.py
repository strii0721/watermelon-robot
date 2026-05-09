import numpy as np

class CameraUtils: 

    _w_T_tcp = np.array([[0, 0, -1, -300], 
                        [-1, 0, 0, -102], 
                        [0, 1, 0, 450], 
                        [0, 0, 0, 1]])
    
    _tcp_T_c = np.array([[-1, 0, 0, 25], 
                         [0, -1, 0, 60], 
                         [0, 0, 1, 10], 
                         [0, 0, 0, 1]])
    
    @classmethod
    def _get_marix_wTtcp(cls) -> np.array: 

        return CameraUtils._w_T_tcp
    
    @classmethod
    def _get_marix_tcpTc(cls) -> np.array: 

        return CameraUtils._tcp_T_c
    
    @classmethod
    def get_world_coordinate(cls, 
                             camera_coordinate: list) -> list: 
        
        w_T_tcp = CameraUtils._get_marix_wTtcp()
        tcp_T_c = CameraUtils._get_marix_tcpTc() 

        target_c = np.append(camera_coordinate, 1.0).reshape(4, 1)

        target_w = (w_T_tcp @ tcp_T_c) @ target_c
        
        world_coordinate = target_w[0:3, 0].tolist()

        return world_coordinate
