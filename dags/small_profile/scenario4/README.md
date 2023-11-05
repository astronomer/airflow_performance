# Scenario 4: Multiple DAGs 1

## DAG Set
<!--- CASE_TABLE_START -->
| Property                | Value           |
|:------------------------|:----------------|
| id                      | 4               |
| name                    | Multiple DAGs 1 |
| dag_files               | 1               |
| dags_per_file           | [10, 50, 100]   |
| tasks_per_dag           | 10              |
| dag_shape               | linear          |
| max_active_runs_per_dag | 1               |
| parallelism             | 128             |
| total_dagruns_per_dag   | 1               |
<!--- CASE_TABLE_END -->

## Environment

| Environment | Executor   | Scheduler AUs | Worker Count | Worker AUs | Extra Capacity AUs | Webserver AUs |
|-------------|------------|---------------|--------------|------------|--------------------|---------------|
| 1           | Local      | 5             | 0            | 0          | 0                  | 5             |
| 2           | Local      | 10            | 0            | 0          | 0                  | 5             |
| 3           | Celery     | 5             | 1            | 10         | 0                  | 5             |
| 4           | Celery     | 10            | 1            | 10         | 0                  | 5             |
| 7           | Kubernetes | 5             | 0            | 0          | 10                 | 5             |
| 8           | Kubernetes | 10            | 0            | 0          | 10                 | 5             |


## Benchmark

Run the Benchmark for each Environment (1-8) and fill the table below:

| Case | DAGs per File | Avg DagRun Duration | Scheduler Lag | Queuing time |
|------|---------------|---------------------|---------------|--------------|
| 1    | 10            |                     |               |              |
| 2    | 50            |                     |               |              |
| 3    | 100           |                     |               |              |

where:

- **Avg DagRun Duration** is the average Duration of all DagRuns
- **Scheduler Lag** is the time between recorded end date of one task and start date of next (taking in to
account max(end_date) of all upstream tasks etc.)
- **Queuing time** is the time between scheduler putting state to queued and task starting (need to make
sure this only makes sense when we are not at queue capacity. i.e. no point recording this if we have 200 tasks but only 16 executor slots.)
* Max (infinite) Dag Concurrency
