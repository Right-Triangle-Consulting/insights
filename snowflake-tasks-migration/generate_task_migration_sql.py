import re


def _parse_task_and_dependents(task_sql):
    expr_1 = 'create or replace task'
    task_name = re.findall(f'{expr_1} .*', task_sql)[0].replace(expr_1, '').strip()
    expr_2 = r"after.*as"
    dependent_list = re.findall(expr_2, task_sql, re.DOTALL)
    if dependent_list:
        dependent_list = dependent_list[0].replace('after', '').replace('as', '').strip().split(',')
        dependent_list = list(map(lambda x: x.strip(), dependent_list))
    return {'task_name': task_name, 'dependents': dependent_list, 'sql': task_sql}


def _get_task_ddl(snow_cxn, task_name, db, schema):
    sql_for_obj = f" select get_ddl('task', '{db}.{schema}.{task_name}', true) as q; "
    sql_definition = snow_cxn.sql(sql_for_obj).collect()
    for row in sql_definition:
        row = row.as_dict()
        t_details = _parse_task_and_dependents(row['Q'])
        t_details['sql'] = row['Q']
        
        return t_details


def _get_all_tasks_in_schema(snow_cxn, db_name, schema_name):
    task_list = []
    sql = f""" show tasks in SCHEMA {db_name}.{schema_name}; """
    obj_results = snow_cxn.sql(sql).collect()
    for o in obj_results:
        o = o.as_dict()
        task_obj = _get_task_ddl(o['name'], db_name, schema_name)
        task_list.append(task_obj)

    return task_list


def _update_existing_ordered_tasks(ordered_tasks, task_list):
    o_idx = 0
    while o_idx < len(ordered_tasks):
        o_deps = list(filter(lambda x: x['task_name'] == ordered_tasks[o_idx], task_list))[0]['dependents']
        deps_in_list = ordered_tasks[o_idx:]
        intersect_values = set(o_deps).intersection(deps_in_list)
        if intersect_values:
            idx_values = list(map(lambda x: ordered_tasks.index(x), intersect_values))
            max_idx = max(idx_values)
            v = ordered_tasks.pop(o_idx)
            ordered_tasks.insert(max_idx, v)
        else:
            o_idx += 1
    
    return ordered_tasks


def _create_task_order(task_list):
    ordered_tasks = []
    for o in task_list:
        if not ordered_tasks:
            ordered_tasks.append(o['task_name'])
        else:
            # if the task has 0 dependencies, put it at the top of the list
            if len(o['dependents']) == 0:
                ordered_tasks.insert(0, o['task_name'])

            else:
                intersect_values = set(ordered_tasks).intersection(set(o['dependents']))
                if intersect_values:
                    idx_values = map(lambda x: ordered_tasks.index(x), intersect_values)
                    max_idx = max(idx_values)
                else:
                    max_idx = len(ordered_tasks)
                ordered_tasks.insert(max_idx + 1, o['task_name'])

            ordered_tasks = _update_existing_ordered_tasks(ordered_tasks, task_list)

    return ordered_tasks


def generate_task_sql(snow_cxn, db, schema):
    tasks = _get_all_tasks_in_schema(snow_cxn, db, schema)
    ordered_tasks = _create_task_order(tasks)

    task_sql = []
    for o in ordered_tasks:
        sql = list(filter(lambda x: x['task_name'] == o, tasks))[0]['task_sql']
        task_sql.append(sql)

    print('\n\n'.join(task_sql))

