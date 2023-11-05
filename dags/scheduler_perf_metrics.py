"""
Deploy this DAG and Trigger it manually. The last task ("find_lags") of the DAG compiles all the LOGs of the
previous 3 tasks and uploads it to https://www.file.io/. Please capture the URL of this uploaded file
from the logs of the last task ("find_lags").

Note: The link to uploaded file is a disposable link i.e it can only be open onced, it won't work after that.
      So please don't open the link.
"""
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
from pprint import pprint
from statistics import mean, stdev
from typing import Dict, List, Optional
from airflow.models import Variable, Connection

import requests
from airflow import DAG, settings
from airflow.configuration import conf
from airflow.models import DagModel, DagBag, DagRun, TaskInstance, XCom
from airflow.models.baseoperator import BaseOperator
from airflow.operators.python import PythonOperator

from airflow.utils.dates import days_ago
from airflow.utils.db import create_session
from airflow.version import version
from sqlalchemy import func, distinct, create_engine
import json
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

AIRFLOW_SLACKWEBHOOK = os.getenv("AIRFLOW_SLACKWEBHOOK", "dummy")


def get_airflow_configs_fn():
    """Get Airflow Configs impacting Performance"""
    configs = {
        "AIRFLOW__SCHEDULER__PARSING_PROCESSES": conf.get('scheduler', 'parsing_processes'),
        "AIRFLOW__CORE__EXECUTOR": conf.get('core', 'executor'),
        "AIRFLOW__CORE__MAX_ACTIVE_RUNS_PER_DAG": conf.get('core', 'max_active_runs_per_dag'),
        "AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG": conf.get('core', 'max_active_tasks_per_dag'),
        "AIRFLOW__CORE__PARALLELISM": conf.get('core', 'parallelism'),
        "AIRFLOW__CELERY__SYNC_PARALLELISM": conf.get('celery', 'sync_parallelism', fallback=None),
        "AIRFLOW__SCHEDULER__SCHEDULER_IDLE_SLEEP_TIME": conf.get(
            'scheduler', 'scheduler_idle_sleep_time', fallback=None),
    }


    pprint(configs, indent=4)

    return configs


def find_lags_fn(**context):
    """Find Total & Average Lag for TIs. Also store Lag Per DagRun"""
    # Get last 100 DagRuns
    with create_session() as session:
        last_100_dags_runs: List[DagRun] = (
            session.query(DagRun)
            .filter(DagRun.end_date != None, ~DagRun.dag_id.in_(["scheduler_perf_metrics", "init_dag"]))
            .order_by(DagRun.execution_date.desc())
            .limit(100)
            .all()
        )

    ti_lag_all_dags = []
    time_in_queued_state_all_dags = []

    # Track Lags per DagRun grouped by DAG
    per_dagrun_lag = defaultdict(dict)

    print(f"last 100 dag runs {last_100_dags_runs}")

    for dr in last_100_dags_runs:
        results = get_avg_task_lags_for_task_in_a_dagrun(dr)
        print(f"results are {results}")
        if not results:
            continue
        task_lags = [result["delay"] for result in results]
        print(f"tasks lags are {task_lags}")
        tasks_time_in_queued_state = [
            result["time_in_queued_state"] for result in results
        ]
        print(f"tasks_time_in_queued_state {tasks_time_in_queued_state}")
        mean_task_lag_for_dr = (
            mean(avg_task_lag.total_seconds() for avg_task_lag in task_lags)
            if task_lags
            else None
        )
        print(f"mean_task_lag_for_dr {mean_task_lag_for_dr}")
        mean_tasks_time_in_queued_state_for_dr = (
            mean(
                task_time_in_queued_state.total_seconds()
                for task_time_in_queued_state in tasks_time_in_queued_state
            )
            if tasks_time_in_queued_state
            else None
        )
        print(f"mean_tasks_time_in_queued_state_for_dr {mean_tasks_time_in_queued_state_for_dr}")

        # Dont save DRs with "None" lag
        if mean_task_lag_for_dr and mean_tasks_time_in_queued_state_for_dr:
            per_dagrun_lag[dr.dag_id][str(dr.execution_date)] = {
                "total_lag": round(mean_task_lag_for_dr, 4),
                "time_in_queued_state": round(
                    mean_tasks_time_in_queued_state_for_dr, 4
                ),
            }

            print("Mean Lag for DagRun (DagId: '%s' | Execution Date: '%s') "
                  "is %.4fs (Time in Executor Queue: %.4fs)" % (dr.dag_id,
                                                                dr.execution_date,
                                                                mean_task_lag_for_dr,
                                                                mean_tasks_time_in_queued_state_for_dr))

        ti_lag_all_dags.extend(task_lags)
        time_in_queued_state_all_dags.extend(tasks_time_in_queued_state)


    if not ti_lag_all_dags:
        print("No eligible TIs found to calculate Lag")
        return

    # Timedelta to seconds
    ti_lag_all_dags = [til.total_seconds() for til in ti_lag_all_dags]
    print(f"ti_lag_all_dags {ti_lag_all_dags}")
    time_in_queued_state_all_dags = [
        tie.total_seconds() for tie in time_in_queued_state_all_dags
    ]
    print(f"time_in_queued_state_all_dags {time_in_queued_state_all_dags}")
    ti_lag_data = {
        "mean": mean(ti_lag_all_dags),
        "stdev": stdev(ti_lag_all_dags),
        "sum": sum(ti_lag_all_dags),
        "count": len(ti_lag_all_dags),
    }
    time_in_queued_state_data = {
        "mean": mean(time_in_queued_state_all_dags),
        "stdev": stdev(time_in_queued_state_all_dags),
        "sum": sum(time_in_queued_state_all_dags),
        "count": len(time_in_queued_state_all_dags),
    }



    print(
        "Average TI Lag across %d tasks is %.4fs (±%.3fs)"
        % (ti_lag_data["count"], ti_lag_data["mean"], ti_lag_data["stdev"])
    )
    print(
        "Average Time In Queued State across %d tasks is %.4fs (±%.3fs)"
        % (
            time_in_queued_state_data["count"],
            time_in_queued_state_data["mean"],
            time_in_queued_state_data["stdev"],
        )
    )



    per_dagrun_lag_dict = dict(per_dagrun_lag)

    print("Lag Per DagRun:")
    pprint(per_dagrun_lag_dict, indent=4, width=1)


    context['ti'].xcom_push(key="ti_lag_data", value=ti_lag_data)
    # Push Per DagRun Lag to XCom
    context["ti"].xcom_push(key="per_dagrun_lag", value=per_dagrun_lag_dict)

    # Push 'Summary of Time in Queued State' to XCom
    context['ti'].xcom_push(key="time_in_queued_state_summary", value=time_in_queued_state_data)

    return ti_lag_data


def get_avg_task_lags_for_task_in_a_dagrun(
        dagrun: DagRun,
) -> List[Dict[str, timedelta]]:
    dag_id = dagrun.dag_id
    print(f"dag id is {dag_id}")
    dag = get_dag(dag_id)
    print(f"dag is {dag}")
    if not dag:
        return []
    tasks = dag.tasks
    print(f"tasks are {tasks}")

    ti_lag = []
    tis: Dict[str, TaskInstance] = {
        ti.task_id: ti for ti in dagrun.get_task_instances()
    }
    print(f"tis are {tis}")
    for task in tasks:
        delay = get_task_schedule_delay(task, tis)
        print(f"delay is {delay}")
        if delay:
            ti = tis[task.task_id]
            print(f"ti values is {ti}")
            if not ti.queued_dttm:
                continue
            print(f"ti start date {ti.start_date}")
            print(f"ti queueddtm {ti.queued_dttm}")
            time_in_queued_state = ti.start_date - ti.queued_dttm
            ti_lag.append(
                {"delay": delay, "time_in_queued_state": time_in_queued_state}
            )

    return ti_lag


@lru_cache(maxsize=128)
def get_dag(dag_id) -> DAG:
    with create_session() as session:
        dag_model = (
            session.query(DagModel).filter(DagModel.dag_id == dag_id).one_or_none()
        )
    return DagBag(dag_model.fileloc).get_dag(dag_id)


def get_task_schedule_delay(
        task: BaseOperator, tis: Dict[str, TaskInstance]
) -> Optional[timedelta]:
    """Find the delay for a single TI"""
    ti = tis[task.task_id]
    print(f"ti is {ti}")
    upstream_tasks = task.upstream_list
    print(f"upstream task are {upstream_tasks}")
    if not upstream_tasks:
        print("no upstream")
        return None

    if not ti.start_date:
        print("no ti start date")
        return None

    upstream_tis = [tis[upstream_task.task_id] for upstream_task in upstream_tasks]
    print(f"upstream tis {upstream_tis}")
    if not upstream_tis:
        return None

    upstream_ti_end_dates = [
        upstream_ti.end_date
        for upstream_ti in upstream_tis
        if isinstance(upstream_ti.end_date, datetime)
    ]
    print(f"upstream end dates {upstream_ti_end_dates}")
    if not upstream_ti_end_dates:
        return None

    max_upstream_ti_end_date = max(upstream_ti_end_dates)
    print(f"max_upstream_ti_end_date {max_upstream_ti_end_date}")
    print(f"ti start date {ti.start_date}")
    if max_upstream_ti_end_date > ti.start_date:
        # This happens for some of the tasks when using Branching with DummyOperators
        return None
    ti_lag = ti.start_date - max_upstream_ti_end_date
    print(f"ti lag is {ti_lag}")
    return ti_lag


def get_usage_stats_fn():
    """Get Statistics of the Deployment. Example: Number of DAGs, Number of TaskInstances etc"""
    with create_session() as session:
        num_dags = session.query(func.count("*")).select_from(DagModel).filter(
            ~DagModel.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).scalar()
        num_dagruns = session.query(func.count("*")).select_from(DagRun).filter(
            ~DagRun.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).scalar()
        num_tis = session.query(func.count("*")).select_from(TaskInstance).filter(
            ~TaskInstance.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).scalar()
        failed_tis = session.query(func.count("*")).select_from(TaskInstance).filter(
            TaskInstance.state == 'failed').filter(
            ~TaskInstance.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).scalar()
        tasks_per_dag_q = (
            session.query(
                TaskInstance.dag_id.label("dag_id"),
                func.count(distinct(TaskInstance.task_id)).label("num_tasks"),
            )
            .group_by(TaskInstance.dag_id)
            .subquery()
        )

        tasks_per_dag_results = session.query(
            func.count("*"), func.avg(tasks_per_dag_q.c.num_tasks)
        ).one_or_none()

        num_dags_atleast_ran_once = tasks_per_dag_results[0]
        avg_num_tasks_per_dag = float(tasks_per_dag_results[1])

    results = {
        "num_dags": num_dags,
        "num_dagruns": num_dagruns,
        "num_tis": num_tis,
        "failed_tis": failed_tis,
        "num_dags_atleast_ran_once": num_dags_atleast_ran_once,
        "avg_num_tasks_per_dag": avg_num_tasks_per_dag,
    }


    print("Summary of Usage: ")
    pprint(results, indent=4)

    return results


def send_logs_fn(**context):
    """Send the logs of the upstream 3 tasks via https://www.file.io/"""

    task_logs_dict: Dict[str, Optional[str]] = {}
    dag_run: DagRun = context["dag_run"]
    task_id = context["task"].task_id

    upstream_tis: Dict[str, TaskInstance] = {
        ti.task_id: ti for ti in dag_run.get_task_instances() if ti.task_id != task_id
    }

    logger = logging.getLogger("airflow.task")
    if conf.has_option("core", "task_log_reader"):
        task_log_reader = conf.get("core", "task_log_reader")
    elif conf.has_option("logging", "task_log_reader"):
        task_log_reader = conf.get("logging", "task_log_reader")
    else:
        raise Exception("task_log_reader not found in 'logging' and 'core' section")

    handler = next(
        (handler for handler in logger.handlers if handler.name == task_log_reader),
        None,
    )

    def _get_logs_with_metadata(ti: TaskInstance, metadata=None):
        metadata = metadata or {}
        if ti is None:
            logs = ["*** Task instance did not exist in the DB\n"]
            metadata["end_of_log"] = True
        else:
            ti.task = perf_dag.task_dict[ti.task_id]
            logs, metadatas = handler.read(ti, ti.try_number - 1, metadata=metadata)
            metadata = metadatas[0]
        return logs, metadata

    for u_task_id, u_ti in upstream_tis.items():
        logs, _ = _get_logs_with_metadata(u_ti)
        task_logs_dict[u_task_id] = logs[0]

    log_msg = "".join(task_logs_dict.values())

    r = requests.post("https://file.io/?expires=3", data={"text": log_msg})
    json_resp = r.json()
    print(json_resp)
    if "link" in json_resp:
        print("Link to uploaded file: ", json_resp["link"])
    return json_resp["link"]


def push_results():
    runtime_version = Variable.get("runtime_version")
    ex_date = DagRun.find(dag_id='scheduler_perf_metrics')[-1].execution_date
    per_dagrun_lag = json.dumps(XCom.get_many(execution_date=ex_date, key='per_dagrun_lag').first().value, indent=3)
    ti_lag_data_summary = json.dumps(
        XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['find_lags']).first().value, indent=3)
    time_in_queued_state_summary = json.dumps(
        XCom.get_many(execution_date=ex_date, key='time_in_queued_state_summary').first().value, indent=3)
    usage_stats = json.dumps(
        XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['get_usage_stats']).first().value, indent=3)
    airflow_configs = json.dumps(
        XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['get_airflow_configs']).first().value,
        indent=3)
    lag_values = json.loads(ti_lag_data_summary)
    q_values = json.loads(time_in_queued_state_summary)

    output_list = [
        f"Performance task lag results generated for:\n\n"
        f"*version*: {version}\n"
        f"*Mean all task lag*: {lag_values['mean']:.2f}s \n",
        f"*Mean all task queued time*: {q_values['mean']:.2f}s \n",
        f"*Total tasks*: {lag_values['count']} \n ",
        f"*usage stats are*: {usage_stats} \n"
        f"*configurations values are *: {airflow_configs} \n ",

    ]
    print(output_list)
    conn = Connection(
        conn_id="slack_conn",
        conn_type="slackwebhook",
        password=AIRFLOW_SLACKWEBHOOK,

    )  # create a connection object

    session = settings.Session()
    connection = session.query(Connection).filter_by(conn_id=conn.conn_id).one_or_none()
    if connection is None:
        logging.info("Connection %s doesn't exist.", str(conn.conn_id))
    else:
        session.delete(connection)
        session.commit()
        logging.info("Connection %s deleted.", str(conn.conn_id))

    session.add(conn)
    session.commit()  # it will insert the connection object programmatically.
    logging.info("Connection slack_conn is created")

    try:
        SlackWebhookOperator(
            task_id="slack_alert",
            slack_webhook_conn_id="slack_conn",
            message="".join(output_list),
            channel="#airflow-regression-results",
            username="airflow_app",
        ).execute(context=None)
    except Exception as exception:
        logging.exception("Error occur while sending slack alert.")
        raise exception



with DAG(
        "scheduler_perf_metrics",
        start_date=days_ago(1),
        max_active_runs=1,
        schedule_interval=None,
        doc_md=__doc__,
) as perf_dag:
    get_airflow_configs = PythonOperator(
        task_id="get_airflow_configs",
        python_callable=get_airflow_configs_fn,
    )

    get_usage_stats = PythonOperator(
        task_id="get_usage_stats",
        python_callable=get_usage_stats_fn,
    )


    find_lags = PythonOperator(
            task_id="find_lags",
            python_callable=find_lags_fn,
        )



    push_results = PythonOperator(
        task_id="push_results",
        python_callable=push_results,
        provide_context=True,
    )



    get_airflow_configs >> find_lags >> get_usage_stats >> push_results