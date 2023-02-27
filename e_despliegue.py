import a_funciones as funciones  ###archivo de funciones propias
import pandas as pd ### para manejo de datos
import sqlite3 as sql
import joblib
import openpyxl ## para exportar a excel


###### el despliegue consiste en dejar todo el código listo para una ejecucion automática en el periodo definido:
###### en este caso se ejecutara el proceso de entrenamiento y prediccion anualmente.
if __name__=="__main__":


    ### conectarse a la base de datos ###
    conn=sql.connect("db_empleados")
    cur=conn.cursor()

    ### Ejecutar sql de preprocesamiento inicial y juntarlo 
    #### con base de preprocesamiento con la que se entrenó para evitar perdida de variables por conversión a dummies

    funciones.ejecutar_sql('preprocesamientos2.sql',cur) ### con las fechas actualizadas explicativas 2023- predecir 2024

    df=pd.read_sql('''select 0 as perf_2023,  * from base_completa2
                    union all
                    select * from base_completa''',conn)

    df.shape
    df[df["perf_2023"]==0].count()
    df.info()

    ####Otras transformaciones en python (imputación, dummies y seleccion de variables)
    df_t= funciones.preparar_datos(df)


    ##Cargar modelo y predecir
    m_lreg = joblib.load("m_lreg.pkl")
    predicciones=m_lreg.predict(df_t)


    ###Crear base con predicciones ####

    pd_pred=pd.DataFrame(predicciones[:4472])
    pd_pred.shape
    ID_emp=df[df["perf_2023"]==0]["EmpID2"]
    perf_pred=pd.concat([ID_emp,pd_pred],axis=1)
    perf_pred.columns=["EmpID","pred_perf_2024"]


    ####LLevar a BD para despliegue 
    perf_pred.to_sql("perf_pred",conn,if_exists="replace")

    ####ver_predicciones_bajas ###
    pred_bajo=perf_pred.sort_values(by=["pred_perf_2024"],ascending=True).head(10)
    emp_pred_bajo= pred_bajo.index
    
    pred=df_t[df_t.index.isin( emp_pred_bajo)]
    pred.loc['coeficientes']= m_lreg.coef_
    m_lreg.intercept_
    pred=pred.T

    pred.to_excel("prediccion.xlsx")
    
    predic=m_lreg.predict(df_t[df_t.index==3947])







    


