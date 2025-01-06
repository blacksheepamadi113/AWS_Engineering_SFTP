from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
# Assuming the above functions are in a helper python file
from sftp_src import upload_files_to_s3_from_sftp 


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
}


dag = DAG(
    dag_id='sftp_to_s3_transfer',
    default_args=default_args,
    description='DAG to transfer files from an SFTP server to S3',
    schedule_interval=None,  # Run manually
    catchup=False  
)
transfer_files_to_s3 = PythonOperator(
    task_id='transfer_files_to_s3',
    python_callable=upload_files_to_s3_from_sftp,
    op_kwargs={
        'sftp_directory': '/path/to/sftp/files',
        's3_bucket': 'your-s3-bucket-name',
        's3_directory': 'path/to/s3/directory'
    },
    dag=dag,
)