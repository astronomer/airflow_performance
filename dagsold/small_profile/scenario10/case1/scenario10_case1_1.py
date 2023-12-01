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
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_2",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_2:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_3",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_3:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_4",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_4:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_5",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_5:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_6",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_6:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_7",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_7:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_8",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_8:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_9",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_9:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])

with DAG(
    os.path.splitext(os.path.basename(__file__))[0] + "_10",
    max_active_runs=1,
    schedule_interval="@daily",
    start_date=days_ago(1),
    end_date=days_ago(1),
    catchup=True,
    concurrency=1000000,
) as dag_10:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, "10")]),
            bash_command="echo test",
        )
        for i in range(1, 10 + 1)
    ]
    for i in range(1, len(tasks)):
        tasks[i].set_upstream(tasks[(i - 1) // 2])
