
#### Cargar paquetes siempre al inicio
from platform import python_version ## versión de python
import pandas as pd ### para manejo de datos
import sqlite3 as sql #### para bases de datos sql



python_version() ### verificar version de python


####################################################################################################################
########################  1. Comprender y limpiar datos ##################################################################
####################################################################################################################
########   Verificar lectura correcta de los datos
########   Datos faltantes (eliminar variables si es necesario)
########   Tipos de variables (categoricas/numéricas/fechas)
########   Niveles en categorícas 
########   Observaciones por categoría
########   Datos atípicos en numéricas


### Cargar tablas de datos desde github ###


action=("data//tbl_Action.csv")  
employees=("data//tbl_Employee.csv")  
performance=("data//tbl_Perf.csv")   

action='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Action.csv'
employees= 'https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Employee.csv'
performance='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Perf.csv'

df_action=pd.read_csv(action)
df_employees=pd.read_csv(employees)
df_performance=pd.read_csv(performance)

###### Verificar lectura correcta de los datos

df_action.sort_values(by=['EffectiveDt'],ascending=0).head(10)
df_employees.sort_values(by=['EngDt'],ascending=0).head(5)
df_performance.sort_values(by=['PerfDate'],ascending=0).head(10)


##### resumen con información tablas faltantes y tipos de variables y hacer correcciones

df_action.info()
df_employees.info()
df_performance.info()

#### Convertir campos a formato fecha 
df_action["EffectiveDt"]=pd.to_datetime(df_action['EffectiveDt'])

df_employees["EngDt"]=pd.to_datetime(df_employees['EngDt'])
df_employees["TermDt"]=pd.to_datetime(df_employees['TermDt'])
df_employees["DOB"]=pd.to_datetime(df_employees['DOB'])

df_performance["PerfDate"]=pd.to_datetime(df_performance['PerfDate'])

#### convertir a categórica
df_action=df_action.astype({'ActionID': object})
df_employees=df_employees.astype({'DepID': object})



###Eliminar filas que no se utilicen
df_employees=df_employees.drop(["PayRate","MgrID","RaceID"], axis=1) # PayRate no tiene datos, MgrID no se va a usar es el código del jefe, RaceID se va a usar la descripción




#### crear base de datos para manejo de datos ####

conn= sql.connect("db_empleados") ### crea una base de datos con el nombre dentro de comillas, si existe crea una conexión.

### Llevar tablas a base de datos

df_action.to_sql("action",conn,if_exists="replace")
df_employees.to_sql("employee",conn,if_exists="replace")
df_performance.to_sql("performance",conn,if_exists="replace")


##### verificar categorías y observaciones ######
#####El número de categorías de una variable influye mucho en la eficiencia y sobre ajust#
### convertir tabla de base de datos en data frame de pandas y hacer consultas ####

read_df_action=pd.read_sql("""
                           select ActionID,count(*) from action
                           group by ActionID""", conn)

read_df_employee=pd.read_sql("""select DepID,count(*) 
                            from employee 
                            group by DepID""", conn)

read_df_employee=pd.read_sql("""select GenderID,count(*) 
                            from employee 
                            group by GenderID""", conn)

read_df_employee=pd.read_sql("""select Level,count(*) 
                            from employee 
                            group by Level""", conn)



cur=conn.cursor() ### para ejecutar querys sql en base de datos create y drop table

cur.execute(" drop table if exists employee2")
cur.execute("""create table employee2 as select *, CASE
                          WHEN Level<10 THEN "<10"
                          WHEN  Level<20 THEN "10-20"
                            ELSE "20-30" END as level2
                            from employee """)

read_df_employee=pd.read_sql("""select Level2,count(*) 
                            from employee2 
                            group by Level2""", conn)

### se debe borrar lacolumna Level


#### para analizar fechas esxtrayendo mes año o día
read_df_performance=pd.read_sql("""select strftime('%d', PerfDate) as D, count(*) from performance group by D""", conn)





####################################################################################################################
########################  1. Análisis exploratorio ##################################################################
####################################################################################################################
