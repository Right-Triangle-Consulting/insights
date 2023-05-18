import json
import pytest
import generate_task_migration_sql as g


task_ddl = [
    ("""create or replace task DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_HEADER_DENIAL_REASON_MPLS
	        warehouse=NONPROD_WH
	        schedule='3400 MINUTES'
	        as 
                CALL DB_STAGE.SCH_STAGE.SP_INSERT_LOAD_HEADER_XDEF_FILE_MPLS('.*xDef_DenialReasons.*');
    """, 
    {'task_name': 'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_HEADER_DENIAL_REASON_MPLS', 
     'dependents': []}),
    ("""create or replace task DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_PLAN
	        warehouse=NONPROD_WH
	        after 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_STAGE_XDEF_PLAN_MPLS
	        as 
                CALL DB_CURATED.SCH_INTEGRATION.SP_INSERT_SAT_MPLS_PLAN();
    """, 
    {'task_name': 'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_PLAN', 
     'dependents': ['DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_STAGE_XDEF_PLAN_MPLS']}),
    ("""create or replace task DB_CURATED.SCH_INTEGRATION.TASK_SP_FINISH_CLAIM_MED_PROF_MPLS
	        warehouse=NONPROD_WH
	        after 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_CLAIM_PROF_MPLS, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_MEMBER_CLAIM_LINE_PROF_MPLS, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_SERVICING_FACILITY_PROVIDER_CLAIM_PROF_MPLS, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LINK_CLAIM_LINE_PROF_MPLS, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_LINE_PROF_DELETE, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_LINE_PROF_EFF, 
                DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_PROF_DELETE
            as 
                CALL SP_FINISH_CLAIM_MED_PROF_MPLS();
    """, 
    {'task_name': 'DB_CURATED.SCH_INTEGRATION.TASK_SP_FINISH_CLAIM_MED_PROF_MPLS', 
     'dependents': [
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_CLAIM_PROF_MPLS', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_MEMBER_CLAIM_LINE_PROF_MPLS', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_HUB_SERVICING_FACILITY_PROVIDER_CLAIM_PROF_MPLS', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LINK_CLAIM_LINE_PROF_MPLS', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_LINE_PROF_DELETE', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_LINE_PROF_EFF', 
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_SAT_MPLS_CLAIM_PROF_DELETE'
    ]})
]
@pytest.mark.parametrize("task_sql", task_ddl)
def test_parse_task_and_dependencies(task_sql):
    parse_results = g._parse_task_and_dependents(task_sql[0])
    assert parse_results == task_sql[1]

ordered_task_list = [
    ([
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_STAGE_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_START_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_HEADER_XDEF_PLAN_MPLS'
      ], 
      [
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_HEADER_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_START_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_LOAD_XDEF_PLAN_MPLS',
        'DB_CURATED.SCH_INTEGRATION.TASK_SP_INSERT_STAGE_XDEF_PLAN_MPLS'
      ])
]

@pytest.mark.parametrize("ordered_task_list", ordered_task_list)
def test_update_existing_ordered_tasks(ordered_task_list):
    t_list = json.load(open('./snowflake-tasks-migration/tests/test_task_list.json', 'r'))
    updated_ordered_list = g._update_existing_ordered_tasks(ordered_task_list[0], t_list)
    assert updated_ordered_list == ordered_task_list[1]