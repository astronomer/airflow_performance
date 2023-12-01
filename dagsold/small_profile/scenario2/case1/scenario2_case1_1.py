import os

from airflow.models.dag import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_1",
    max_active_runs=5,
    schedule_interval="@daily",
    start_date=days_ago(5),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_1:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "100")]),
            bash_command="echo test",
        )
        for i in range(1, 100 + 1)
    ]
    chain(*tasks)
