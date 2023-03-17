create schema row_access_demo;

create or replace TABLE EMPLOYEE (
	EMPLOYEE_ID INT,
	EMPLOYEE_NAME VARCHAR,
	EMPLOYEE_TITLE VARCHAR,
	EMPLOYEE_DEPARTMENT VARCHAR
);

insert into employee values 
(1, 'Mary Jones', 'President', 'EXECUTIVE'),
(2, 'Susan Brown', 'Chief People Officer', 'HR'),
(3, 'Nala Stone', 'Sofware Engineering Manager', 'ENGINEER'),
(4, 'Yana Blythe', 'Software Engineer', 'ENGINEER'),
(5, 'Wanda Delin', 'Director', 'SALES'),
(6, 'Jana Stuart', 'Sales Manager', 'SAaaLES'),
(7, 'Belinda Smith', 'Sales Manager', 'SALES'),
(8, 'Ana Lopez', 'Sales Manager', 'SALES');


create or replace TABLE SALARY (
	EMPLOYEE_ID INT,
	SALARY FLOAT,
	BEGIN_DATE TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
	END_DATE TIMESTAMP_TZ DEFAULT NULL
);

insert into salary values
(1, 200000, '2010-01-10', null),
(2, 150000, '2011-01-10', null),
(3, 125000, '2010-01-15', null),
(4, 100000, '2010-01-10', null),
(5, 100000, '2020-03-10', null),
(6, 60000, '2010-01-10', null),
(7, 70000, '2015-04-10', null),
(8, 65000, '2010-01-10', null);


create or replace TABLE DEPT_PERMISSIONS (
    DEPT_PERMISSION VARCHAR(255),
    DEPARTMENT_NAME VARCHAR(255)
);

insert into DEPT_PERMISSIONS values
('EG', 'ENGINEER'),
('SL', 'SALES'),
('HR', 'HR'),
('HR', 'EXECUTIVE'),
('HR', 'SALES'),
('HR', 'ENGINEER')

create view v_employee_salary as (
    select 
        e.employee_name,
        e.employee_title,
        e.employee_department,
        s.salary
    from
        employee e
        left join salary s on s.employee_id = e.employee_id
    where end_date is null
);


CREATE ROLE RA_DATA_ACCESS;
GRANT ROLE RA_DATA_ACCESS to role SYSADMIN;
grant usage on warehouse demo_wh to role RA_DATA_ACCESS;
grant usage on database jh_demo to role RA_DATA_ACCESS;
grant usage on schema row_access_demo to role RAD_DATA_ACCESS;
grant select on view row_access_demo.v_employee_salary to role RAD_DATA_ACCESS;
GRANT SELECT ON table row_access_demo.dept_permissions to role RAD_DATA_ACCESS;
CREATE ROLE RA_HR_MANAGER;
GRANT ROLE RA_HR_MANAGER to role SYSADMIN;
grant role RA_DATA_ACCESS to role RAD_HR_MANAGER;
CREATE ROLE RA_EG_MANAGER;
GRANT ROLE RA_EG_MANAGER to role SYSADMIN;
grant role RA_DATA_ACCESS to role RAD_EG_MANAGER;
CREATE ROLE RA_SL_MANAGER;
GRANT ROLE RA_SL_MANAGER to role SYSADMIN;
grant role RA_DATA_ACCESS to role RAD_SL_MANAGER;


create or replace row access policy rad_department_permissions as (dept varchar) returns boolean ->
    exists (
            select 1 from dept_permissions
              where 
                current_role() = 'RAD_' || dept_permission || '_MANAGER'
                and department_name = dept
          );

ALTER VIEW v_employee_salary
  ADD ROW ACCESS POLICY rad_department_permissions ON (employee_department);


-- Queries to test
use role rad_sales_MANAGER;
select * from v_employee_salary;

use role rad_eng_MANAGER;
select * from v_employee_salary;

use role rad_hr_MANAGER;
select * from v_employee_salary;
