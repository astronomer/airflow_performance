import os

from airflow.models.dag import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_1",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_1:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    chain(*tasks)
