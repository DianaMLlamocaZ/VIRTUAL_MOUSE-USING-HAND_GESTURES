import matplotlib.pyplot as plt
import json

#Graficar smoothed vs no smoothed coordinates
def graficar_smoothed(path_smoothed,path_real):
    with open(f"{path_smoothed}_x.json","r") as f1, open(f"{path_smoothed}_y.json","r") as f2:
        data_smoothed_x=json.load(f1)
        data_smoothed_y=json.load(f2)

    with open(f"{path_real}_x.json","r") as f1, open(f"{path_real}_y.json","r") as f2:
        data_real_x=json.load(f1)
        data_real_y=json.load(f2)


    #Ventana 1
    plt.figure(1)   
    plt.title("Eje X -- Coordenadas Smoothed vs Real")
    plt.plot(data_real_x,color="b",label="Real Data")
    plt.plot(data_smoothed_x,color="r",label="Smoothed Data")
    

    plt.legend()


    #Ventana 2   
    plt.figure(2)
    plt.title("Eje Y -- Coordenadas Smoothed vs Real")
    plt.plot(data_real_y,color="b",label="Real Data")
    plt.plot(data_smoothed_y,color="r",label="Smoothed Data")
    

    plt.legend()


    plt.show()


#Graficar invariance scale vs no invariance scale:
#Debido a que están en diferentes escalas, aplicaré la normalización "min-max" para que ambos compartan escalas comunes SIN
#alterar la distribución de los datos, que es importante mantener para observar el patrón original
def graficar_invariance(path_inv,path_inv_no_sm,path_no_inv):
    with open(path_inv,"r") as f1, open(path_inv_no_sm) as f2,open(path_no_inv,"r") as f3:
        data_inv=json.load(f1)
        data_inv_no_sm=json.load(f2)
        data_no_inv=json.load(f3)


        max_data_inv,min_data_inv=max(data_inv),min(data_inv)
        max_data_inv_no_sm,min_data_inv_no_sm=max(data_inv_no_sm),min(data_inv_no_sm)
        max_data_no_inv,min_data_no_inv=max(data_no_inv),min(data_no_inv)
        eps=1e-6 #evitar div entre 0 por si acaso


        data_inv_norm=[(data-min_data_inv)/(max_data_inv-min_data_inv+eps) for data in data_inv]
        data_inv_norm_no_sm=[(data_no_sm-min_data_inv_no_sm)/(max_data_inv_no_sm-min_data_inv_no_sm+eps) for data_no_sm in data_inv_no_sm]
        data_no_inv_norm=[(data_no-min_data_no_inv)/(max_data_no_inv-min_data_no_inv+eps) for data_no in data_no_inv]


        #Ventana 1
        plt.figure(figsize=(10,5))
        plt.title("Distancia Invarianza vs No Invarianza")
        plt.plot(data_no_inv_norm,color="b",label="Distancia No Invarianza Norm Smoothed")
        plt.plot(data_inv_norm_no_sm,color="r",label="Distancia Invarianza Norm No Smoothed")
        plt.plot(data_inv_norm,color="g",label="Distancia Invarianza Norm Smoothed")
    
        plt.legend()
        plt.show()

#Unccoment para realizar las gráficas luego de haber utilizado el mouse virtual
#graficar_smoothed("./results_graphics/grafica_smoothed","./results_graphics/real")
#graficar_invariance(path_inv="./results_graphics/distancia_invarianza.json",path_inv_no_sm="./results_graphics/distancia_invarianza_no_smoothed.json",path_no_inv="./results_graphics/distancia_no_invarianza_smoothed.json")
