import cv2
import numpy as np


class KalmanFilter:
    def __init__(self):
        self.kalman_filter=cv2.KalmanFilter(dynamParams=4,measureParams=2)

        self.kalman_filter.transitionMatrix=np.array([
            [1,0,1,0],
            [0,1,0,1],
            [0,0,1,0],
            [0,0,0,1]
        ],dtype=np.float32)

        self.kalman_filter.measurementMatrix=np.array([
            [1,0,0,0],
            [0,1,0,0]
        ],dtype=np.float32)
        
        self.kalman_filter.processNoiseCov=np.eye(N=4,M=4,dtype=np.float32)*1e-5        #Se confía más en la fórmula
        self.kalman_filter.measurementNoiseCov=np.eye(N=2,M=2,dtype=np.float32)*1e-2    #No se confía tanto en el sensor



    #Inicializar en la coordenada inicial: Solo se actualiza el statePost, ya que "predict" utiliza ese vector en
    #conjunto a la matriz de transición
    def initialize(self,x_init,y_init):
        
        state_pre_coord=np.array([[x_init],[y_init],[0],[0]],dtype=np.float32)
        self.kalman_filter.statePost=state_pre_coord
        


    #Predicción usando el filtro de kalman
    def predict(self):

        pred_coord=self.kalman_filter.predict()

        return pred_coord



    #Correct
    def correct(self,x,y):

        coord=np.array([[x],[y]],dtype=np.float32)
        correct_coord=self.kalman_filter.correct(coord)
        
        return correct_coord
