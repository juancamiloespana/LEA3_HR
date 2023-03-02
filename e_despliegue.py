import a_funciones as funciones  ###archivo de funciones propias
import pandas as pd ### para manejo de datos
import sqlite3 as sql
import joblib
import openpyxl ## para exportar a excel
import numpy as np


###### el despliegue consiste en dejar todo el código listo para una ejecucion automática en el periodo definido:
###### en este caso se ejecutara el proceso de entrenamiento y prediccion anualmente.
if __name__=="__main__":


    ### conectarse a la base de datos ###
    conn=sql.connect("db_empleados")
    cur=conn.cursor()

    ### Ejecutar sql de preprocesamiento inicial y juntarlo 
    #### con base de preprocesamiento con la que se entrenó para evitar perdida de variables por conversión a dummies

    funciones.ejecutar_sql('preprocesamientos2.sql',cur) ### con las fechas actualizadas explicativas 2023- predecir 2024
    df=pd.read_sql('''select  * from base_completa2''',conn)

  
    ####Otras transformaciones en python (imputación, dummies y seleccion de variables)
    df_t= funciones.preparar_datos(df)


    ##Cargar modelo y predecir
    m_lreg = joblib.load("m_lreg.pkl")
    predicciones=m_lreg.predict(df_t)
    pd_pred=pd.DataFrame(predicciones, columns=['pred_perf_2024'])


    ###Crear base con predicciones ####

    perf_pred=pd.concat([df['EmpID2'],df_t,pd_pred],axis=1)
   
    ####LLevar a BD para despliegue 
    perf_pred.loc[:,['EmpID2', 'pred_perf_2024']].to_sql("perf_pred",conn,if_exists="replace") ## llevar predicciones a BD con ID Empleados
    

    ####ver_predicciones_bajas ###
    emp_pred_bajo=perf_pred.sort_values(by=["pred_perf_2024"],ascending=True).head(10)
    
    emp_pred_bajo.set_index('EmpID2', inplace=True) 
    pred=emp_pred_bajo.T
    
    coeficientes=pd.DataFrame( np.append(m_lreg.intercept_,m_lreg.coef_) , columns=['coeficientes'])  ### agregar coeficientes
   
    pred.to_excel("prediccion.xlsx")   #### exportar predicciones mas bajas y variables explicativas
    coeficientes.to_excel("coeficientes.xlsx") ### exportar coeficientes para analizar predicciones
    








    


