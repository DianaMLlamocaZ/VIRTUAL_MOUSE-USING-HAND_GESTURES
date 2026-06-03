import numpy as np

def scale_invariance(list_kps):
    kps_array=[[landmark.x,landmark.y,landmark.z] for landmark in list_kps]
    kps_array=np.array(object=kps_array)
    
    wrist=kps_array[0] #wrist (coordenada base)
        
    dist_vct=kps_array[0]-kps_array[9]
    dist_norm=np.linalg.norm(dist_vct)
    
    keypoints_rel=kps_array-wrist #coordenada relativa
    
    keypoints_norm=keypoints_rel/dist_norm
    
    return keypoints_norm
