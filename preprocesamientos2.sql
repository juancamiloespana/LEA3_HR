
----Los comentarios en sql se ponen con --
---después de finalizar cada consulta se pone ;

------ se filtran empleados que no tengan evaluación de 2023 porque se retiraron antes de la evaluación y los que no tenían antes de 2023 porque entraron ese año

drop table if exists performance2;

create table  performance2 as 
select
EmpID2,
--avg (case when strftime('%Y',PerfDate) = '2023' then Rating2 else null end) as perf_2023,
avg (case when strftime('%Y',PerfDate) = '2023' then Rating2 else null end) as perf_2022,
avg( case when strftime('%Y',PerfDate)  = '2023' then null else Rating2 end) as avg_perf
from performance
group by EmpID2
having perf_2022 is not null ---entraron después 2023 se filtran
--and perf_2022 is not null -- 

;


----se modifica tabla de acciones para que quede un registro por empleado ---

drop table if exists action2;

create table action2 as

with t1 as
(
select
EmpID2,
count(*) as cnt_total,
--sum(case when ActionID = 10 then 1  else 0 end ) as cnt_mov10, --se eliminan porque no fueron relevantes
--sum(case when ActionID = 30 then 1  else 0 end ) as cnt_mov30,
--sum(case when ActionID = 90 then 1  else 0 end ) as cnt_mov90,
--sum(case when ActionID = 91 then 1  else 0 end ) as cnt_mov91,
max(EffectiveDt) as lst_mov
from action

where strftime('%Y',EffectiveDt) <= '2023'
group by EmpID2
)
select
EmpID2,
--cnt_total,
--cnt_mov10,
--cnt_mov30,
--cnt_mov90,
--cnt_mov91,
JulianDay('2023-12-31') - JulianDay(lst_mov) as dias_lst_mov
 from t1;


 ----recategorizar tabla employee calcular variables nuevas
drop table if exists employee2;

create table employee2 as select
EmpID2,
JulianDay('2023-12-31')-JulianDay(EngDt) as antiguedad_dias,
DepID,
GenderID,
JulianDay('2023-12-31')-JulianDay(DOB) as edad_dias,
CASE
WHEN Level<10 THEN "<10"
WHEN  Level<20 THEN "10-20"
ELSE "20-30" END as level2,
MaritalDesc,
FromDiversityJobFairID,
PayRate2,
case when trim(Position) in ('IT Manager - Support',
'Director of Operations',
'President & CEO',
'Data Architect',
'CIO',
'Enterprise Architect',
'Software Engineering Manager',
'BI Director',
'Data Analyst',
'IT Director',
'Director of Sales',
'Principal Data Architect',
'IT Manager - Infra') then 'Others' else trim(position)
end as position,
case when trim(State) in ('MA','TX','CT','AZ','ID','CO','TN','KY') 
then trim(State) else 'Others'
end as State,
CitizenDesc,
Case when trim(HispanicLatino) ="no" then "No"
when HispanicLatino ="yes" then "Yes"
else trim(HispanicLatino) end as HispanicLatino,
RaceDesc,
case when trim(RecruitmentSource) in (
'On-line Web application',
'Company Intranet - Partner',
'Careerbuilder',
'Information Session',
'Pay Per Click') then 'Others' else trim(RecruitmentSource)
end as RecruitmentSource,
EngagementSurvey,
EmpSatisfaction,
SpecialProjectsCount
from employee;


----crear tabla de análisis final -----


drop table if exists base_completa2;

create table base_completa2 as 
select 
--a.perf_2023,
a.perf_2022,
a.avg_perf,
--b.cnt_total,
--b.cnt_mov10,
--b.cnt_mov30,
--b.cnt_mov90,
--b.cnt_mov91,
b.dias_lst_mov,
c.*
from performance2 a inner join action2 b on a.EmpID2=b.EmpID2
inner join employee2 c on a.EmpID2=c.EmpID2
















