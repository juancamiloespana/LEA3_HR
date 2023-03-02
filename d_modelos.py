
import pandas as pd ### para manejo de datos
import sqlite3 as sql

import a_funciones as funciones  ###archivo de funciones propias
from sklearn import linear_model ## para regresión lineal
from sklearn import tree ###para ajustar arboles de decisión
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor ##Ensamble con bagging
from sklearn.ensemble import GradientBoostingRegressor ###Ensamble boosting
from sklearn.model_selection import cross_val_predict, cross_val_score, cross_validate
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error

import numpy as np
import matplotlib.pyplot as plt ### gráficos
from sklearn.model_selection import RandomizedSearchCV
import joblib  ### para guardar modelos
from sklearn.preprocessing import StandardScaler ## escalar variables 
import openpyxl


#### conectarse a base de datos preprocesada

conn=sql.connect("db_empleados")

#### traer bd preprocesada para iniciar modelo ####


df=pd.read_sql("select * from base_completa  ",conn)
df.info()
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
df2=df.dropna(axis=0) ### si se pone 1 se borra la columna con na si se pone 0, o se deja vacío, se borra la fila
df2.info()


#### imputación para variables categóricas y numéricas
##se separan columnas categóricas o que se quieran tratar así de las numéricas

list_cat=['DepID', 'GenderID', 'level2','MaritalDesc','FromDiversityJobFairID','position', 'State', 'CitizenDesc', 'HispanicLatino', 'RaceDesc',
       'RecruitmentSource']

df3=funciones.imputar_f(df,list_cat)
df3.info()


## d. convertir a dummys

list_dummies=['DepID', 'level2','MaritalDesc','position', 'State', 'CitizenDesc', 'HispanicLatino', 'RaceDesc',
       'RecruitmentSource']

df_dummies=pd.get_dummies(df3,columns=list_dummies)
df_dummies.info()

#####  tipos de tratamiento de categóricas: label encoding(Variable respuesta), ordinal encoding (explicativas), one hot ecoding-get_dummies
###label encoding
#gato 1
#perro 2
#oso 3

### dep =1  -> 0
### dep =5  -> 1
#### dep = 8 -> 2



### label encoding: solo target variable
### ordinal encoding: solo variables explicativas categóricas ordinales
### one hot encoding: variables explicativas categóricas nominales

### ordinal
#### bajo = 1
#### medio =2
#### alto = 3

 ##Nominal (no funciona con ordinal, se debe aplicar one-hotencoding)
#### casdo = 1
#### divorciado=2
#### soltero = 3


######### seleccion de modelos candidatos:

##### se seleccionará Decision trees y linear regression por su fácil interpretabilidad
##### se utilizarán dos ensambles uno con bagging: randomforest y uno con boosting gradient boosting 

#### Shaloww learning

###weak learners:  RL, arbol de decisión
### ensamble: Random forest:

#### cantidad: más datos modelo complejo
#### modelo complejo con poquitos datos -> sobreajuste

### deep learning


######## con base en los modelos candidatos se realizará una selección de variables ########

y=df_dummies.perf_2023
X1= df_dummies.loc[:,~df_dummies.columns.isin(['perf_2023','EmpID2'])]
scaler=StandardScaler()
scaler.fit(X1)
X2=scaler.transform(X1)
X=pd.DataFrame(X2,columns=X1.columns)


m_lreg = linear_model.LinearRegression()
m_rtree=tree.DecisionTreeRegressor()
m_rf= RandomForestRegressor()
m_gbt=GradientBoostingRegressor()

modelos=list([m_lreg,m_rtree, m_rf, m_gbt])

var_names=funciones.sel_variables(modelos,X,y,threshold="1.7*mean")
var_names.shape



## var1  4
## var 5
### var 3
### importancia promedio 4.4

##threshold indica el valor que debe superar la importancia de variables para ser seleccionada
###"mean" significa  que tiene que superar el promedio "1.2*mean" tiene que superar a la media por el 20%


X2=X[var_names] ### matriz con variables seleccionadas
X2.info()
X.info()

#####después de seleccionar variables, seleccionar el mejor modelo #######
#### se prueba con la base full y con la base con variables seleccionadas

## K fold cross validation   10 ()  1,  9  ---2 (1,3:9)

rmse_df=funciones.medir_modelos(modelos,"neg_root_mean_squared_error",X,y,10) ## base con todas las variables 
rmse_varsel=funciones.medir_modelos(modelos,"neg_root_mean_squared_error",X2,y,10) ### base con variables seleccionadas


rmse=pd.concat([rmse_df,rmse_varsel],axis=1)
rmse.columns=['rl', 'dt', 'rf', 'gb',
       'rl_Sel', 'dt_sel', 'rf_sel', 'gb_Sel']

rmse_df.plot(kind='box') #### gráfico para modelos todas las varibles
rmse_varsel.plot(kind='box') ### gráfico para modelo variables seleccionadas
rmse.plot(kind='box') ### gráfico para modelos sel y todas las variables

rmse.mean() ### medias de mape





#############Hiperparameter tunning - no aplica para reg lineal #################3

param_grid = [{'n_estimators': [3, 500, 100], 'max_features': [5,20],
               'min_samples_split': [100, 20, 5]}]

##n_estimator numero de arboles de decisiones
##max feratures numero de variables analizadas para la participacion de nodos del arbol
## min_samples_split: mínimo de observaciones que pueden quedar en un nodo

 

tun_rf=RandomizedSearchCV(m_rf,param_distributions=param_grid,n_iter=6,scoring="neg_root_mean_squared_error")
tun_rf.fit(X2,y)
### se comenta porque toma mucho tiempo en ejecutar

pd.set_option('display.max_colwidth', 100)
resultados=tun_rf.cv_results_
tun_rf.best_params_
pd_resultados=pd.DataFrame(resultados)
pd_resultados[["params","mean_test_score"]].sort_values(by="mean_test_score", ascending=False)

rf_final=tun_rf.best_estimator_ ### Guardar el modelo con hyperparameter tunning
m_lreg=m_lreg.fit(X2,y)





### función para exportar y guardar objetos de python (cualqueira)

joblib.dump(rf_final, "rf_final.pkl") ## 
joblib.dump(m_lreg, "m_lreg.pkl") ## 
joblib.dump(list_cat, "list_cat.pkl") ### para realizar imputacion
joblib.dump(list_dummies, "list_dummies.pkl")  ### para convertir a dummies
joblib.dump(var_names, "var_names.pkl")  ### para variables con que se entrena modelo
joblib.dump(scaler, "scaler.pkl") ## 


rf_final = joblib.load("rf_final.pkl")
m_lreg = joblib.load("m_lreg.pkl")
list_cat=joblib.load("list_cat.pkl")
list_dummies=joblib.load("list_dummies.pkl")
var_names=joblib.load("var_names.pkl")
scaler=joblib.load("scaler.pkl") 

###### evaluar modelos afinados finales ###########

#####Evaluar métrica de entrenamiento y evaluación para mirar sobre ajuste ####

eval=cross_validate(rf_final,X2,y,cv=5,scoring="neg_root_mean_squared_error",return_train_score=True)
eval2=cross_validate(m_lreg,X2,y,cv=5,scoring="neg_root_mean_squared_error",return_train_score=True)


#### convertir resultado de evaluacion entrenamiento y evaluacion en data frame para RF
train_rf=pd.DataFrame(eval['train_score'])
test_rf=pd.DataFrame(eval['test_score'])
train_test_rf=pd.concat([train_rf, test_rf],axis=1)
train_test_rf.columns=['train_score','test_score']

#### convertir resultado de evaluacion entrenamiento y evaluacion en data frame para RL
train_rl=pd.DataFrame(eval2['train_score'])
test_rl=pd.DataFrame(eval2['test_score'])
train_test_rl=pd.concat([train_rl, test_rl],axis=1)
train_test_rl.columns=['train_score','test_score']

train_test_rl["test_score"].mean()
train_test_rf["test_score"].mean()


##### comparación con predicciones actuales  ############

mse=mean_squared_error(df['perf_2023'], df['perf_2022'])
rmse= mse**(0.5)



####Mirar la distribución de los errores para no quedarse solo con medida resumen

predictions=cross_val_predict(m_lreg,X2,y,cv=5)

pred=pd.DataFrame(predictions,columns=['pred'])
pdy=y.to_frame()
error=pdy['perf_2023']-pred['pred']
error.hist(bins=50, grid=False)



plt.boxplot(error,vert=False)
plt.show()


predictions2=cross_val_predict(rf_final,X2,y,cv=5)

pred2=pd.DataFrame(predictions2,columns=['pred'])
error2=pdy['perf_2023']-pred2['pred']
error2.hist(bins=50, grid=False)


plt.boxplot(error2,vert=False)
plt.show()


##### Mirar importancia de variables para tomar acciones ###
pd.set_option('display.max_rows', 100)
importancia1=pd.DataFrame( m_lreg.feature_names_in_)
importancia2=pd.DataFrame(m_lreg.coef_)
importancia=pd.concat([importancia1,importancia2],axis=1)
importancia.columns=["variable","peso"]


importancia.sort_values(by=["peso"], ascending=False)
importancia.to_excel("feature_importances.xlsx")
m_lreg.predict(X2[X2.index==0])