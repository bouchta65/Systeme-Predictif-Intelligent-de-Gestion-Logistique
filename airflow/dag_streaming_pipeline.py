from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'streaming_pipeline',
    start_date=datetime(2025, 11, 20),
    schedule_interval=None,
    catchup=False,
    tags=['streaming']
)

check_services = BashOperator(
    task_id='check_services',
    bash_command='docker ps | grep -E "postgres|mongodb|fastapi|bridge|spark-streaming"',
    dag=dag
)

start_pipeline = BashOperator(
    task_id='start_pipeline',
    bash_command='docker compose up -d fastapi bridge spark-streaming',
    dag=dag
)

monitor_logs = BashOperator(
    task_id='monitor_logs',
    bash_command='docker logs spark-streaming --tail 50',
    dag=dag
)

check_services >> start_pipeline >> monitor_logs
