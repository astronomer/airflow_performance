import os
from datetime import date
import time
import pandas as pd

#import pygsheets
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.session import create_session
from airflow.models import DagRun, TaskInstance, DagModel, Variable
from sqlalchemy import func, text
from airflow.decorators import task
from airflow.models.param import Param
import pendulum
from airflow.version import version

results_data = {"AIRFLOW_VERSION": "9.1.0", "BASE_IMAGE": "base-9.1.0", "SCENARIO": "scenario10", "CASE": "case2",
                "SCHEDULERS": "2", "WORKERS": "4"}


def check_for_ti_count():
    with create_session() as session:
        try:
            total_tis = session.query(func.count('*')).select_from(TaskInstance).filter(
                TaskInstance.task_id.like('tasks%'), TaskInstance.state == 'success').scalar()
            return total_tis
        except Exception as e:
            raise e


def unpause_all_dags():
    with create_session() as session:
        try:
            # Use SQLAlchemy's update function with a subquery to unpause DAGs matching the regex pattern
            subquery = text(
                f"UPDATE dag "
                f"SET is_paused = :unpaused "
                f"WHERE dag_id LIKE :pattern"
            )
            session.execute(subquery, {"unpaused": False, "pattern": "thput%"})
            session.commit()
        except Exception as e:
            session.rollback()
            raise e


def get_all_db_records_count():
    with create_session() as session:
        try:
            total_tis = session.query(func.count('*')).select_from(TaskInstance).scalar()
            total_dr = session.query(func.count('*')).select_from(DagRun).scalar()
            total_dgm = session.query(func.count('*')).select_from(DagModel).scalar()
            # total_tis = session.query(func.count('*')).select_from(TaskInstance).filter(TaskInstance.task_id.like('tasks%'),TaskInstance.state == 'success').scalar()
            str_full = "DB Strength:TIs-" + str(total_tis) + "DRs-" + str(total_dr) + "Dags-" + str(total_dgm)
            return str_full
        except Exception as e:
            raise e


def run_throughput_dag():
    print()
    print("#####################################################################")
    print("Waiting for all DAGRuns to be completed to run Performance Lag DAG ...")
    print("#####################################################################")
    print()
    DIFF_COUNT_TOTAL = 0
    now = "$(date +'%d_%m_%Y_%s')"
    # FILENAME="task_throughput_results_" + now + ".csv"
    print("Exported File:")
    print("TOTAL,DIFF_COUNT_TOTAL,DIFF_COUNT")
    print("Creating test scenario/case results file for Task Throughput")

    throughput_values = []
    for i in range(1, 500):
        unpause_all_dags()
        time.sleep(30)
        # print( "2.Check DB Count & Print")
        NUM_TASKS_BEGIN = check_for_ti_count()
        # print( "3.Sleep 2 minutes")
        time.sleep(120)
        # print( "4.Check DB Count & Print")
        NUM_TASKS_END = check_for_ti_count()
        # print( "--------------------")
        DIFF_COUNT = NUM_TASKS_END - NUM_TASKS_BEGIN
        print(get_all_db_records_count() + "   Throughput per minute " + str(DIFF_COUNT / 2))
        throughput_values.append(DIFF_COUNT)

    # Calculate the sum of all the throughput values
    sum_throughput = sum(throughput_values)

    # # Calculate the average throughput
    average_throughput = sum_throughput / len(throughput_values)

    # # Print the average throughput
    print(average_throughput / 2)
    data_series = pd.Series(throughput_values)

    # Calculate the maximum and minimum using the max() and min() methods
    mean_value = data_series.mean()
    max_value = data_series.max()
    min_value = data_series.min()
    worker_machine_type = os.environ["AIRFLOW__WORKER_MACHINE_TYPE"]

    # push_to_google_sheet(
    #     [date.today().strftime("%d/%m/%Y"), "Astro", version, str(worker_machine_type), str(mean_value), str(max_value),
    #      str(min_value), str(throughput_values[0]), str(throughput_values[-1])])
    # Plot the throughput values
    # df = pd.DataFrame({'throughput': throughput_values})
    # df.plot(x='index', y='throughput')


# def push_to_google_sheet(audit_data: list[str]):
#     credentials_file = '/usr/local/airflow/dags/service-account-gcp.json'
#     sheet_name = 'Airflow Task Throughput - Astro vs MWAA'
#     gc = pygsheets.authorize(service_file=credentials_file)
#     sh = gc.open(sheet_name)
#     google_sheet = sh.worksheet_by_title("astro_vs_MWAA_2.6.3")
#     try:
#         google_sheet.append_table(values=audit_data, start="A1", overwrite=False)
#         print("Data updated successfully!")
#     except KeyError:
#         pass


default_args = {
    'owner': 'ernest',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        'throughput_dag',
        default_args=default_args,
        start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
        params={
            "AIRFLOW_VERSION": Param("9.1.0", type="string"),
            "SCENARIO": Param("scenario10", type="string"),
            "CASE": Param("case2", type="string"),
            "SCHEDULERS": Param("2", type="string"),
            "WORKERS": Param("4", type="string"),
        },
        description='Dag to run Throughput test',
        schedule_interval=None,
        max_active_tasks=15,
) as dag:
    @task
    def set_variables():
        for key, value in results_data.items():
            Variable.set(key, f"{{ params.{key} }}")


    run_test_task_throughput = PythonOperator(
        task_id='run_throughput_dag',
        python_callable=run_throughput_dag,
        dag=dag,
    )

set_variables() >> run_test_task_throughput
