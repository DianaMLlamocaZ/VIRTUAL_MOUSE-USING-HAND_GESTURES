#Librerías
import cv2
import mediapipe as mp
import numpy as np
import pyautogui as pag
import math
from utils import scale_invariance
from save_data_plot import save_json
import json

#Instancio objetos
draw_kps=mp.solutions.drawing_utils
hands_arc=mp.solutions.hands

#Hands class
hands_class=hands_arc.Hands(max_num_hands=1)


#Pantalla original
width_screen,height_screen=pag.size()


#Size frame
size_frame=(640,640)


#Escalado
x_factor,y_factor=width_screen/size_frame[0],height_screen/size_frame[1]


#Diccionario que almacena los valores x_prev, y_prev para el smoothing del movimiento del cursor
movement_coord_prev={"index":[0,0],"thumb":[0,0]}
movement_coord_inv_prev={"index":[0,0],"thumb":[0,0]}


#Variable hold_click para evitar realizar clicks continuamente
hold_click=False


#Alpha hyperparameter para el smoothing del movimiento
alpha=0.3 #0.22


#Smoothing Graphic - Index Finger
smoothing_x,smoothing_y=[],[]
real_x,real_y=[],[]


#Gráfica de distancia - Invarianza a escala NO Smoothed vs Invarianza a escala Smoothed VS no invarianza Smoothed
dist_invarianza=[]  #--> esta es la distancia con invarianza Y smoothed
dist_invarianza_no_smoothed=[]
dist_no_invarianza_smoothed=[]


#Variable para evitar errores al inicio si los dedos aparecen juntos
x_prev_safe=None


#Cámara
camara=cv2.VideoCapture(0)

click_det=False

#Bucle
with hands_class as hands_model:
    while True:    
        ret,frame=camara.read()
        frame_rsz=cv2.resize(src=frame,dsize=(size_frame[0],size_frame[1]))

        frame_flip=cv2.flip(src=frame_rsz,flipCode=1)
        frame_flip_rgb=cv2.cvtColor(src=frame_flip,code=cv2.COLOR_BGR2RGB)


        #Predicciones
        predicciones=hands_model.process(frame_flip_rgb)

        #Landmarks
        landmarks_preds=predicciones.multi_hand_landmarks   #landmarks de ambas manos (Si hay) --> por eso es un iterable, cada 1 con sus kps
        hand_detected=predicciones.multi_handedness
        if hand_detected:
            hand_detected_now=hand_detected[0].classification[0].label


        #Si hay landmarks detectados, se dibujan. El cursor es la mano izquierda
        if landmarks_preds:   
            for landmarks in landmarks_preds:
                draw_kps.draw_landmarks(frame_flip,landmarks,hands_arc.HAND_CONNECTIONS)

                list_kps=landmarks.landmark
                kps_inv_escala=scale_invariance(list_kps)
                

                #Left hand cursor
                if hand_detected_now=="Left":
                    
                    #REESCALAR LANDMARK 4: Fingertip del dedo pulgar (thumb finger) --> Se obtiene SOLO para GRÁFICA
                    x_4,y_4=list_kps[4].x,list_kps[4].y
                    x_thumb_scaled_frame,y_thumb_scaled_frame=x_4*frame_rsz.shape[1],y_4*frame_rsz.shape[0]
                    cv2.circle(img=frame_flip,center=(int(x_thumb_scaled_frame),int(y_thumb_scaled_frame)),radius=2,color=(0,255,0),thickness=2)                        

                    x_final_scaled_4,y_final_scaled_4=x_factor*x_thumb_scaled_frame,y_factor*y_thumb_scaled_frame
                    
                        

                    #REESCALAR LANDMARK 8: Fingertip del dedo índice, PUNTERO MOVEMENT
                    x_8,y_8=list_kps[8].x,list_kps[8].y
                    x_indice_scaled_frame,y_indice_scaled_frame=x_8*frame_rsz.shape[1],y_8*frame_rsz.shape[0]
                    cv2.circle(img=frame_flip,center=(int(x_indice_scaled_frame),int(y_indice_scaled_frame)),radius=2,color=(0,255,0),thickness=2)
                            
                    x_final_scaled_8,y_final_scaled_8=x_factor*x_indice_scaled_frame,y_factor*y_indice_scaled_frame
                    



                    #SMOOTHING THUMB de coordenadas NO INVARIANTES (solo para gráficas, porque en realidad se usan las coordenadas invariantes + smoothed)
                    current_x_smoothed_thumb=(1-alpha)*movement_coord_prev["thumb"][0]+alpha*x_final_scaled_4
                    current_y_smoothed_thumb=(1-alpha)*movement_coord_prev["thumb"][1]+alpha*y_final_scaled_4


                    #SMOOTHING ÍNDICE de coordenadas NO INVARIANTES --> Se usa para el movimiento del cursor
                    current_x_smoothed_index=(1-alpha)*movement_coord_prev["index"][0]+alpha*x_final_scaled_8
                    current_y_smoothed_index=(1-alpha)*movement_coord_prev["index"][1]+alpha*y_final_scaled_8

                    

                    #Muevo el cursor en base a las coordenadas del dedo índice SOLO si NO se hace click (para evitar movement)
                    if not click_det:
                        pag.moveTo(x=current_x_smoothed_index,y=current_y_smoothed_index,_pause=False)


                    
                    #Actualizo el diccionario de movimiento: index y thumb fingers
                    movement_coord_prev["index"][0]=current_x_smoothed_index
                    movement_coord_prev["index"][1]=current_y_smoothed_index

                    movement_coord_prev["thumb"][0]=current_x_smoothed_thumb
                    movement_coord_prev["thumb"][1]=current_y_smoothed_thumb



                    #Se almacenan las coordenadas del dedo índice de las coordenadas smoothed pero no invariantes a escala
                    #y las coordenadas reales para comparar sus gráficas y visualizar el resultados del suavizado
                    smoothing_x.append(current_x_smoothed_index),smoothing_y.append(current_y_smoothed_index)
                    real_x.append(x_final_scaled_8),real_y.append(y_final_scaled_8)



                    #CLICK:                    
                    #===Distancia de los KPS Smootheds, pero NO invariantes a escala (gráfica):
                    dx=abs(movement_coord_prev["index"][0]-movement_coord_prev["thumb"][0])
                    dy=abs(movement_coord_prev["index"][1]-movement_coord_prev["thumb"][1])
                    distancia=math.hypot(dx,dy)             #Distancia calculada a partir de las smoothed coordinates
                    dist_no_invarianza_smoothed.append(distancia)    #Se almacena el valor de la distancia para graficarla



                    #===Distancia de los KPS con invarianza a escala, pero NO smoothed (gráfica):
                    dx_proof_no_sm=abs(kps_inv_escala[8][0]-kps_inv_escala[4][0])
                    dy_proof_no_sm=abs(kps_inv_escala[8][1]-kps_inv_escala[4][1])
                    distancia_proof_escalada_no_sm=math.hypot(dx_proof_no_sm,dy_proof_no_sm)    #Distancia calculada a partir de las coordenadas invariantes a escala
                    dist_invarianza_no_smoothed.append(distancia_proof_escalada_no_sm)          #Se almacena el valor de la distancia para graficarla



                    #===KPS invariantes a escala y SMOOTHED --> Se usa para el CLICK:
                    #-SMOOTHED INDEX:
                    kps_inv_escala_8_x=(1-alpha)*movement_coord_inv_prev["index"][0]+alpha*kps_inv_escala[8][0]
                    kps_inv_escala_8_y=(1-alpha)*movement_coord_inv_prev["index"][1]+alpha*kps_inv_escala[8][1]
                    
                    #-SMOOTHED THUMB:
                    kps_inv_escala_4_x=(1-alpha)*movement_coord_inv_prev["thumb"][0]+alpha*kps_inv_escala[4][0]
                    kps_inv_escala_4_y=(1-alpha)*movement_coord_inv_prev["thumb"][1]+alpha*kps_inv_escala[4][1]

                    
                    dx_proof=abs(kps_inv_escala_8_x-kps_inv_escala_4_x)
                    dy_proof=abs(kps_inv_escala_8_y-kps_inv_escala_4_y)
                    
                    distancia_proof_escalada=math.hypot(dx_proof,dy_proof)
                    dist_invarianza.append(distancia_proof_escalada)        #Se almacena también para graficarlo
                    
                    

                    #Actualización del diccionario que almacena las coordenadas previas inv
                    movement_coord_inv_prev["index"]=[kps_inv_escala_8_x,kps_inv_escala_8_y]
                    movement_coord_inv_prev["thumb"]=[kps_inv_escala_4_x,kps_inv_escala_4_y]
                    


                    #Evito clickear constantemente. Para ello, uso un flag
                    if distancia_proof_escalada<=0.25 and x_prev_safe!=None: #--> A prueba y error, este es el más acertado
                        
                        if not hold_click: #Aquí definir x_prev_safe y y_prev_safe ANTES de esta condicional, sino saldrá error de "not defined" si la distancia inicial está dentro del threshold
                            pag.click(x_prev_safe,y_prev_safe,button="left")
                            hold_click=True
                            click_det=True
                            
                    else:
                        hold_click,click_det=False,False
                        x_prev_safe,y_prev_safe=current_x_smoothed_index,current_y_smoothed_index #--> Se guarda la coordenada ANTES de hacer la seña del click (evita movement)
                       


                #PRUEBA: Scrolling --> Solo si la mano es la derecha
                if hand_detected_now=="Right":
                    
                    #Scrolling event
                    fingertip_index,fingertip_middle=list_kps[8].y*frame_rsz.shape[0],list_kps[12].y*frame_rsz.shape[0]
                    fingerdip_index,fingerdip_middle=list_kps[7].y*frame_rsz.shape[0],list_kps[11].y*frame_rsz.shape[0]
                    
                    
                    #Levantar dedo índice --> Scrolling hacia abajo (solo si el dedo medio NO está levantado)
                    if fingerdip_index>fingertip_index and fingertip_middle>fingerdip_middle:
                        pag.scroll(clicks=-40)
                    
                    #Levantar dedo middle --> Scrolling hacia arriba (solo si el dedo índice NO está levantado)
                    elif fingerdip_middle>fingertip_middle and fingertip_index>fingerdip_index:
                        pag.scroll(clicks=40)

                    


        tecla=cv2.waitKey(1)
        if tecla==ord("q") or not ret:
            break

        cv2.imshow(winname="Frame actual",mat=frame_flip)



#Guardar los valores para el plotteo
#Gráfica Coordenadas Smoothed
names_smoothed=["grafica_smoothed_x","grafica_smoothed_y","real_x","real_y"]
list_data_smoothed=[smoothing_x,smoothing_y,real_x,real_y]

for name_1,data_1 in zip(names_smoothed,list_data_smoothed):
    save_json(name_1,data_1)


#Gráfica distancia invarianza
names_inv=["distancia_invarianza","distancia_invarianza_no_smoothed","distancia_no_invarianza_smoothed"]
data_inv=[dist_invarianza,dist_invarianza_no_smoothed,dist_no_invarianza_smoothed]

for name_2,data_2 in zip(names_inv,data_inv):
    save_json(name_2,data_2)
