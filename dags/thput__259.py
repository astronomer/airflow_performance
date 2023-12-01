from airflow.models.dag import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
from airflow.utils.helpers import chain
with DAG('thput__259_1',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_1:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_2',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_2:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_3',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_3:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_4',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_4:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_5',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_5:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_6',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_6:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_7',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_7:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_8',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_8:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_9',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_9:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_10',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_10:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_11',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_11:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_12',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_12:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_13',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_13:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_14',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_14:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_15',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_15:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_16',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_16:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_17',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_17:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_18',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_18:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_19',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_19:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)

with DAG('thput__259_20',
         max_active_runs=3,
         start_date=days_ago(2),
         schedule_interval="@hourly",
         concurrency=16) as dag_20:
    tasks = [
        BashOperator(
            task_id="__".join(["tasks", "{}_of_{}".format(i, '50')]), bash_command='echo test'
        )
        for i in range(1, 50 + 1)
    ]
    chain(*tasks)
