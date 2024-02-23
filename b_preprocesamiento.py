
#### Cargar paquetes siempre al inicio
import pandas as pd ### para manejo de datos
import sqlite3 as sql #### para bases de datos sql
import a_funciones as funciones  ###archivo de funciones propias
import sys ## saber ruta de la que carga paquetes


###Ruta directorio qué tiene paquetes
sys.path
sys.path.append('c:\\cod\\LEA3_HR\\data') ## este comanda agrega una ruta



####################################################################################################################
########################  1. Comprender y limpiar datos ##################################################################
####################################################################################################################
########   Verificar lectura correcta de los datos
########   Verificar Datos faltantes (eliminar variables si es necesario) (la imputación está la parte de modelado)
########   Tipos de variables (categoricas/numéricas/fechas)
########   Niveles en categorícas 
########   Observaciones por categoría
########   Datos atípicos en numéricas


### Cargar tablas de datos desde github ###

#action=("data//tbl_Action.csv")  
#employees=("data//tbl_Employee.csv")  
#performance=("data//tbl_Perf.csv")   

action='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Action.csv'
employees= 'https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Employee.csv'
performance='https://raw.githubusercontent.com/juancamiloespana/aplicacionesanalitica/main/data/tbl_Perf.csv'

df_action=pd.read_csv(action)
df_employees=pd.read_csv(employees)
df_performance=pd.read_csv(performance)



###### Verificar lectura correcta de los datos

df_action.sort_values(by=['EmpID2'],ascending=1).head(100)
df_employees.sort_values(by=['EngDt'],ascending=0).head(5)
df_performance.sort_values(by=['EmpID2'],ascending=0).head(100)

##### resumen con información tablas faltantes y tipos de variables y hacer correcciones

df_action.info(verbose=True)
df_employees.info()
df_performance.info()

    
#### Convertir campos a formato fecha 
df_action["EffectiveDt"]=pd.to_datetime(df_action['EffectiveDt'] )

df_employees["EngDt"]=pd.to_datetime(df_employees['EngDt'], format="%d/%m/%Y")
df_employees["TermDt"]=pd.to_datetime(df_employees['TermDt'], format="%d/%b/%Y")
df_employees["DOB"]=pd.to_datetime(df_employees['DOB'], format="%d/%b/%Y")

df_performance["PerfDate"]=pd.to_datetime(df_performance['PerfDate'], format="%d/%b/%Y")

#### convertir a categórica
df_action=df_action.astype({'ActionID': object,"ActID": object})
df_employees=df_employees.astype({'DepID': object})

###Eliminar columnas que no se utilicen
df_employees=df_employees.drop(["PayRate","MgrID","RaceID","TermDt"], axis=1) # PayRate no tiene datos, MgrID no se va a usar es el código del jefe, RaceID se va a usar la descripción


#### crear base de datos para manejo de datos ####

conn= sql.connect("data\\db_empleados") ### crea una base de datos con el nombre dentro de comillas, si existe crea una conexión.
cur=conn.cursor() ### ejecutar funciones  en BD


### Llevar tablas a base de datos
df_action.to_sql("action",conn,if_exists="replace")
df_employees.to_sql("employee",conn,if_exists="replace")
df_performance.to_sql("performance",conn,if_exists="replace")


cur.execute("Select name from sqlite_master where type='table'") ### consultar bases de datos
cur.fetchall()

##### verificar categorías y observaciones ######
#####El número de categorías de una variable influye mucho en la eficiencia y sobre ajuste#
### convertir tabla de base de datos en data frame de pandas y hacer consultas ####


pd.read_sql("""select DepID,count(*) 
                            from employee 
                            group by DepID""", conn)

pd.read_sql("""select GenderID,count(*) 
                            from employee 
                            group by GenderID""", conn)

pd.read_sql("""select Level,count(*) 
                            from employee 
                            group by Level""", conn)  ###se debe recategorizar porque tiene muchos niveles y niveles con pocas observaciones

pd.read_sql("""select FromDiversityJobFairID,count(*) 
                            from employee 
                            group by FromDiversityJobFairID""", conn)

pd.read_sql("""select MaritalDesc,count(*) 
                            from employee 
                            group by MaritalDesc""", conn)

pd.read_sql("""select Position ,count(*) as cnt 
                            from employee 
                            group by Position order by cnt desc""", conn) ### existen muchos niveles 


pd.read_sql("""select State ,count(*) as cnt
                            from employee 
                            group by State  order by cnt desc""", conn) 


pd.read_sql("""select CitizenDesc   ,count(*) as cnt
                            from employee 
                            group by CitizenDesc   """, conn) 


pd.read_sql("""select HispanicLatino    ,count(*) as cnt
                            from employee 
                            group by HispanicLatino     """, conn) 


pd.read_sql("""select RaceDesc   ,count(*) as cnt
                            from employee 
                            group by RaceDesc    """, conn) 


pd.read_sql("""select RecruitmentSource  ,count(*) as cnt
                            from employee 
                            group by RecruitmentSource order by cnt desc  """, conn) 





#### para analizar fechas esxtrayendo mes año o día


pd.read_sql("""select strftime('%Y',PerfDate) as fecha, 
                                count(*) as cnt
                                from performance 
                                group by fecha""", conn)

pd.read_sql("""select PerfDate as fecha, 
                                count(*) as cnt
                                from performance 
                                group by fecha""", conn)

#### para analizar fechas esxtrayendo mes año o día
pd.read_sql("""select EffectiveDt  as fecha, 
                                count(*) as cnt
                                from action 
                                group by fecha""", conn)


##### las variables identificadas para recategorizar son: 
####Level, position, state, hispaniclatino, recruitmente source


###### Otros preprocesamientos que se realizarán:

##### 1. Filtrar datos por empleados que tengan evaluación de desempeño en el último año 2023
##### 2. La tabla de acciones se convertirá para que quede un solo registro por empleado
##### 3. Se calularán variables con base en la información de empleados como edad, antiguedad

#### para hacer todos los preprocesamienteos se crea archivo .sql que se ejecuta con la función: ejecutar_sql del archivo funciones.py

funciones.ejecutar_sql('preprocesamientos.sql',cur)

cur.execute("select name from sqlite_master where type='table'")
cur.fetchall()

df=pd.read_sql("select * from base_completa  ",conn)
pd.read_sql("select count(distinct empID2)  from base_completa  ",conn)
df.info()
df.describe(include='all')



