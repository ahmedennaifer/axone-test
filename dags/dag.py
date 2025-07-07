from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable


default_args = {
    "owner": "ahmed-ennaifer",
    "depends_on_past": False,
    "start_date": datetime(2025, 7, 7),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "axone_fb_etl_pipeline",
    default_args=default_args,
    description="ETL pipeline for facebook posts - Axone take home test",
    catchup=False,
)

extract_task = BashOperator(
    task_id="extract_facebook_data",
    # for pipeline testing, we'll only use 1 scroll for airflow. otherwise will take toooo long...
    bash_command='cd /Users/nafra/Desktop/code/perso/axone &&  /opt/homebrew/bin/uv run src/extract.py --query "{{ dag_run.conf.get("query", "deces jacques chirac") }}" --num_scrolls {{ dag_run.conf.get("num_scrolls", 1) }}',
    dag=dag,
    env={"EMAIL": Variable.get("EMAIL"), "PW": Variable.get("PW")},
)


transform_task = BashOperator(
    task_id="transform_data",
    bash_command="cd /Users/nafra/Desktop/code/perso/axone && /opt/homebrew/bin/uv run src/transform.py",
    dag=dag,
)


load_task = BashOperator(
    task_id="load_to_db",
    bash_command="cd /Users/nafra/Desktop/code/perso/axone && /opt/homebrew/bin/uv run python src/load_to_db.py",
    dag=dag,
)


extract_task >> transform_task >> load_task
