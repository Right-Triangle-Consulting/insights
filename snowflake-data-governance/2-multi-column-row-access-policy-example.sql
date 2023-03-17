create table inpatient_medical_claim (
    claim_id varchar,
    claim_line_segment varchar,
    claim_start_date varchar,
    claim_end_date varchar,
    facility varchar,
    payment_amount varchar,
    attending_physician_npi varchar,
    operating_physician_npi varchar,
    admission_date varchar,
    admitting_diagnosis_code varchar,
    discharged_date varchar,
    payer_code varchar
);

create stage sample_medical_claim;

-- you will have to download and use the snowcli in order to do this part
put file:///DE1_0_2008_to_2010_Inpatient_Claims_Sample_1.csv @sample_medical_claim;

-- initially set all the payer codes to be payer_a
copy into inpatient_medical_claim
from
    (
        select
            $2::varchar,
            $3::varchar,
            $4::varchar,
            $5::varchar,
            $6::varchar,
            $7::varchar,
            $9::varchar,
            $10::varchar,
            $12::varchar,
            $13::varchar,
            $20::varchar,
            'PAYER_A'
        from
            @sample_medical_claim   
    )
    FILE_FORMAT = (type=csv, skip_header=1);

create table role_facility_payer (
    role varchar(255),
    facility_id varchar(30),
    payer varchar(20)
);

insert into role_facility_payer 
values 
(upper('demo_payer_a_viewer'), null, 'PAYER_A'),
(upper('demo_payer_b_viewer'), null, 'PAYER_B'),
(upper('demo_payer_c_viewer'), null, 'PAYER_C'),
(upper('demo_facility_3900MB_viewer'), '3900MB', null),
(upper('demo_facility_3913XU_viewer'), '3913XU', null),
(upper('demo_facility_0520ZS_viewer'), '0520ZS', null);

create or replace row access policy rap_claim as (col_facility varchar, col_payer varchar) returns boolean ->
  exists (
	select 1 from 
		role_facility_payer
	where
		(facility_id = col_facility OR payer = col_payer)
		and role = current_role()
);
alter table inpatient_medical_claim add row access policy rap_claim on (facility, payer_code);

create role demo_viewer;
grant role demo_viewer to role sysadmin;
grant usage on database jh_demo to role demo_viewer;
grant usage on all schemas in database jh_demo to role demo_viewer;
grant usage on future schemas in database jh_demo to role demo_viewer;
grant select on all tables in schema jh_demo.row_access_demo to role demo_viewer;
grant select on future tables in schema jh_demo.row_access_demo to role demo_viewer;
grant select on all views in schema jh_demo.row_access_demo to role demo_viewer;
grant select on future views in schema jh_demo.row_access_demo to role demo_viewer;

create role demo_payer_a_viewer;
grant role demo_payer_a_viewer to role sysadmin;
grant role demo_viewer to role demo_payer_a_viewer;

create role demo_payer_b_viewer;
grant role demo_payer_b_viewer to role sysadmin;
grant role demo_viewer to role demo_payer_b_viewer;

create role demo_payer_c_viewer;
grant role demo_payer_c_viewer to role sysadmin;
grant role demo_viewer to role demo_payer_c_viewer;

create role demo_facility_3900MB_viewer;
grant role demo_facility_3900MB_viewer to role sysadmin;
grant role demo_viewer to role demo_facility_3900MB_viewer;
 
create role demo_facility_3913XU_viewer;
grant role demo_facility_3913XU_viewer to role sysadmin;
grant role demo_viewer to role demo_facility_3913XU_viewer;

create role demo_facility_0520ZS_viewer;
grant role demo_facility_0520ZS_viewer to role sysadmin;
grant role demo_viewer to role demo_facility_0520ZS_viewer;

-- diversify the payer code by making some of the claims have payer b and some have payer c
update inpatient_medical_claim set payer_code = 'PAYER_B' where claim_id like '%7';
update inpatient_medical_claim set payer_code = 'PAYER_C' where claim_id like '%7';

-- test out the roles with the dataset
use role demo_payer_a_viewer; 
select distinct payer_code from inpatient_medical_claim;
select * from inpatient_medical_claim;

use role demo_facility_0520zs_viewer;
select distinct facility from inpatient_medical_claim;
select * from inpatient_medical_claim where facility = '0520ZS';