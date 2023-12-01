import time
from airflow import DAG
from airflow.api.common.trigger_dag import trigger_dag
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.session import create_session
from airflow.models import DagRun, TaskInstance, Log, TaskFail, TaskReschedule, DagModel, XCom, Variable
from sqlalchemy import func, update, text
from airflow.decorators import task
from airflow.models.param import Param
import pendulum

results_data = {"runtime_version": "8.9.0", "base_image": "base-8.9.0", "scenario_number": "scenario1",
                "case_number": "case2", "schedulers": "2", "workers": "4"}


def get_perf_results():
    dag_id = "scheduler_perf_metrics"
    dag_run = DagRun.find(dag_id=dag_id)[-1]
    ex_date = dag_run.execution_date
    print('per_dagrun_lag: ', XCom.get_many(execution_date=ex_date, key='per_dagrun_lag').first().value)
    print('ti_lag_data_summary:',
          XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['find_lags']).first().value)
    print('time_in_queued_state_summary:',
          XCom.get_many(execution_date=ex_date, key='time_in_queued_state_summary').first().value)
    print('usage_stats:',
          XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['get_usage_stats']).first().value)
    print('airflow_configs:',
          XCom.get_many(execution_date=ex_date, key='return_value', task_ids=['get_airflow_configs']).first().value)


def clear_database():
    with create_session() as session:
        try:

            session.query(TaskInstance).filter(~TaskInstance.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(
                synchronize_session='fetch')
            session.query(DagRun).filter(~DagRun.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(
                synchronize_session='fetch')
            session.query(Log).filter(~Log.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(
                synchronize_session='fetch')
            session.query(TaskFail).filter(~TaskFail.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(
                synchronize_session='fetch')
            session.query(TaskReschedule).filter(
                ~TaskReschedule.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(synchronize_session='fetch')
            session.commit()
        except Exception as e:
            session.rollback()
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
            session.execute(subquery, {"unpaused": False, "pattern": "scenario%case%"})
            session.commit()
        except Exception as e:
            session.rollback()
            raise e


def trigger_target_dag():
    # Trigger the target DAG
    dag_id = 'scheduler_perf_metrics'  # Replace with your target DAG ID
    trigger_dag(dag_id=dag_id, run_id=None, conf=None, execution_date=None)
    print(f'Triggered DAG: {dag_id}')


def check_for_dagruns():
    with create_session() as session:
        try:
            num_dagruns = (
                session.query(func.count('*'))
                .select_from(DagRun)
                .filter(DagRun.state == 'running')
                .filter(DagRun.dag_id.like('scenario%case%'))
                .scalar()
            )
            print('Number of running DAGs:', num_dagruns)
            tis_by_state = (
                session.query(TaskInstance.state, func.count('*'))
                .select_from(TaskInstance)
                .group_by(TaskInstance.state)
                .filter(TaskInstance.dag_id.like('scenario%case%'))
                .all()
            )
            print('TIs by state:', tis_by_state)
            return num_dagruns
        except Exception as e:
            raise e


def unpause_dag(dag_id):
    with create_session() as session:
        dag = session.query(DagModel).filter(DagModel.dag_id == dag_id).first()
        if dag:
            # Set the DAG's is_paused property to False
            dag.is_paused = False
            session.commit()
            print(f'DAG {dag_id} has been unpaused.')
        else:
            print(f'DAG {dag_id} not found.')


def run_perf_dag():
    time.sleep(10)
    print("#####################################################################")
    print("Waiting for all DAGRuns to be completed to run Performance Lag DAG ...")
    print("#####################################################################")
    for i in range(1, 5001):
        print("------- Check all DAGRuns are completed: -------")
        num_dagruns = check_for_dagruns()
        if num_dagruns == 0:
            unpause_dag('scheduler_perf_metrics')
            trigger_target_dag()
            break
        else:
            print(f"Still Waiting..Iteration: {i}")
        time.sleep(10)


def pause_all_dags():
    with create_session() as session:
        try:
            # Use SQLAlchemy's update function with a subquery to unpause DAGs matching the regex pattern
            subquery = text(
                f"UPDATE dag "
                f"SET is_paused = :unpaused "
                f"WHERE dag_id LIKE :pattern"
            )
            session.execute(subquery, {"unpaused": True, "pattern": "scenario%case%"})
            session.commit()
        except Exception as e:
            session.rollback()
            raise e


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def run_test_task_lag():
    SECONDS = 0
    print("\n##########################################")
    print(f"Executing Clear database")
    print("##########################################")
    clear_database()
    print("Exit Clear database")
    print(f"unpause_selected_dag Scenario1Case2")
    print(f"Scenario1Case2")
    unpause_all_dags()
    print("Unpause dags with pattern Scenario1Case2")
    print("run perf dag")
    run_perf_dag()
    duration = SECONDS
    time.sleep(90)
    get_perf_results()
    print("\n##########################################")
    print(f"Completed Scenario ")
    print(f"Scenario completion Time:{duration // 60} minutes and {duration % 60} seconds.")
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(f"Time: {dt_string}")
    print("##########################################\n\n")
    pause_all_dags()


with DAG(
        'init_dag',
        default_args=default_args,
        start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
        params={
            "runtime_version": Param("9.1.0", type="string"),
            "base_image": Param("base-9.1.0", type="string"),
            "scenario_number": Param("scenario1", type="string"),
            "case_number": Param("case2", type="string"),
            "schedulers": Param("2", type="string"),
            "workers": Param("4", type="string"),
        },
        description='Dag to run perf test on MWAA',
        schedule_interval=None,
        tags=['perf_dag']

) as dag:
    @task
    def set_variables(**kwargs):
        for key, value in results_data.items():
            Variable.set(key, kwargs.get('params').get(key))


    @task
    def tear_down():
        with create_session() as session:
            session.query(DagModel).filter(~DagModel.dag_id.in_(["scheduler_perf_metrics", "init_dag"])).delete(
                synchronize_session='fetch')


    run_test_task_lag_task = PythonOperator(
        task_id='run_test_task_lag',
        python_callable=run_test_task_lag,
        dag=dag,
    )

set_variables() >> run_test_task_lag_task >> tear_down()