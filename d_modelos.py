
import pandas as pd ### para manejo de datos
import sqlite3 as sql

import a_funciones as funciones  ###archivo de funciones propias

from sklearn.impute import SimpleImputer ### para imputación

from sklearn import linear_model ## para regresión lineal
from sklearn import tree ###para ajustar arboles de decisión
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor ##Ensamble con bagging
from sklearn.ensemble import GradientBoostingRegressor ###Ensamble boosting
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.feature_selection import SelectFromModel
import matplotlib.pyplot as plt ### gráficos
from sklearn.model_selection import RandomizedSearchCV

#### conectarse a base de datos preprocesada

conn=sql.connect("db_empleados")


#### traer bd preprocesada para iniciar modelo ####
df=pd.read_sql("select * from base_completa  ",conn)

################################################################
#### Pasos para modelo #########################################
###############################################################

    ### a.crear base final (hecho) ####
    ### b. verificar null  (hecho) ####
    ### c. Imputar o eliminar nulos si es necesario
    ### d. convertir categóricas a dummies 
    ### e. definir modelos a entrenar candidatos
    ### f. seleccionar variables
    ### g. definir modelo ganador
    ### h  afinar hiperparámetros
    


######### c. tratamiento de faltantes

df.info() ### no tiene faltantes pero crearemos unos para trabajar
df.iloc[1,2] =None  ### crear faltante en numérica
df.iloc[1,6] =None  ### crear faltante en categórica
df.info()  

### borrar columnas con na
df2=df.dropna(0) ### si se pone 1 se borra la columna con na si se pone 0 o se deja vacío se borra la fila
df2.info()


#### imputación para variables categóricas y numéricas
##se separan columnas categóricas o que se quieran tratar así de las numéricas

list_cat=['DepID', 'GenderID', 'level2','MaritalDesc','FromDiversityJobFairID','position', 'State', 'CitizenDesc', 'HispanicLatino', 'RaceDesc',
       'RecruitmentSource']

df3=funciones.imputar_f(df,list_cat,SimpleImputer, pd)
df3.info()

## d. convertir a dummys
df_dummies=pd.get_dummies(df3,columns=['DepID', 'level2','MaritalDesc','position', 'State', 'CitizenDesc', 'HispanicLatino', 'RaceDesc',
       'RecruitmentSource'])
df_dummies.info()

######### seleccion de modelos candidatos:

##### se seleccionará Decision trees y linear regression por su fácil interpretabilidad
##### se utilizarán dos ensambles uno con bagging: randomforest y uno con boosting gradient boosting 


######## con base en los modelos candidatos se realizará una selección de variables ########

y=df_dummies.perf_2023
X= df_dummies.loc[:,~df_dummies.columns.isin(['perf_2023','EmpID2'])]


m_lreg = linear_model.LinearRegression()
m_rtree=tree.DecisionTreeRegressor()
m_rf= RandomForestRegressor()
m_gbt=GradientBoostingRegressor()

modelos=list([m_lreg,m_rtree, m_rf, m_gbt])

var_names=funciones.sel_variables(modelos,X,y,SelectFromModel,np,threshold="1.2*mean")
var_names.shape

X2=X[var_names] ### matriz con variables seleccionadas
X2.info()
X.info()

#####después de seleccionar variables, seleccionar el mejor modelo #######
#### se prueba con la base full y con la base con variables seleccionadas

mape_df=funciones.medir_modelos(modelos,"neg_mean_absolute_percentage_error",X,y,10, cross_val_score, pd)
rmse_df=funciones.medir_modelos(modelos,"neg_root_mean_squared_error",X,y,10, cross_val_score, pd)

mape_varsel=funciones.medir_modelos(modelos,"neg_mean_absolute_percentage_error",X2,y,10, cross_val_score, pd)
rmse_varsel=funciones.medir_modelos(modelos,"neg_root_mean_squared_error",X2,y,10, cross_val_score, pd)

mape=pd.concat([mape_df,mape_varsel],axis=1)
mape.columns=['rl', 'dt', 'rf', 'gb',
       'rl_Sel', 'dt_sel', 'rf_sel', 'gb_Sel']

rmse=pd.concat([rmse_df,rmse_varsel],axis=1)
rmse.columns=['rl', 'dt', 'rf', 'gb',
       'rl_Sel', 'dt_sel', 'rf_sel', 'gb_Sel']

mape.plot(kind='box')
rmse.plot(kind='box')

#############Hiperparameter tunning - no aplica para reg lineal #################3

param_grid = [{'n_estimators': [3, 100], 'max_features': [2, 4, 8, 10]},
{'bootstrap': [False,True]}]


tun_rf=RandomizedSearchCV(m_rf,param_distributions=param_grid,n_iter=5,scoring="neg_root_mean_squared_error")
search=tun_rf.fit(X2,y)


tun_rf.best_params_
resultados=tun_rf.cv_results_
pd_resultados=pd.DataFrame(resultados)
pd_resultados[["params","mean_test_score"]]











    
