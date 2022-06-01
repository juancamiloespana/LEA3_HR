
#### Cargar paquetes siempre al inicio
from platform import python_version ## versión de python
import pandas as pd ### para manejo de datos
import sqlite3 as sql #### para bases de datos sql

python_version() ### verificar version de python


####################################################################################################################
########################  Carga de datos ###########################################################################
####################################################################################################################

### Cargar tablas de datos desde github ###
   
action='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Action.csv'
employees= 'https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Employee.csv'
performance='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Perf.csv'

df_action=pd.read_csv(action)
df_employees=pd.read_csv(employees)
df_performance=pd.read_csv(performance)


###### Verificar contenido de tablas

df_action.sort_values(by=['EffectiveDt'],ascending=0).head(10)
df_employees.sort_values(by=['EngDt'],ascending=0).head(10)
df_performance.sort_values(by=['PerfDate'],ascending=0).head(10)

#### crear base de datos ####

conn= sql.connect("db_empleados") ### crea una base de datos con el nombre dentro de comillas, si existe crea una conexión.

### Llevar tablas a base de datos

df_action.to_sql("action",conn,if_exists="replace")
df_employees.to_sql("employee",conn,if_exists="replace")
df_performance.to_sql("performance",conn,if_exists="replace")

### convertir tabla de base de datos en data frame de pandas

read_df_action=pd.read_sql('select ActionID,count(*) from action group by ActionID', conn)
read_df_employee=pd.read_sql('select DepID,count(*) from employee group by DepID', conn)
read_df_performance=pd.read_sql('select DepID,count(*) from employee group by DepID', conn)


####################################################################################################################
########################  Comprender y limpiar datos ##################################################################
####################################################################################################################
########   Verificar lectura correcta de los datos
########   Datos faltantes (eliminar variables)
########   Tipos de variables (categoricas/numéricas)
########   Niveles en categoríacas 
########   Observaciones por categoría
######## 
######## 2. Datos atípicos en numéricas
######## 3. V


