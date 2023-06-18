from datetime import timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonVirtualenvOperator
from airflow.utils.dates import days_ago

DAG_DEFAULT_ARGS = {
    'owner': 'JFAexe',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

s3_server = Variable.get('s3_server')
s3_data = Variable.get('s3_data')


def generate_data(dir_name):
    from pathlib import Path
    from random import choice, random

    import pandas as pd
    from src.constants import (BOOLEAN_TYPES, CONTRACT_TYPES, GENDER_TYPES,
                               INTERNET_DEPENDENT_TYPES,
                               INTERNET_SERVICE_TYPES, MULTIPLE_LINES_TYPES,
                               PAYMENT_METHOD_TYPES)
    from src.prediction_row import DataRow

    def get_float_range(start: float, end: float) -> float:
        return start + random() * (end - start)

    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)

    data = []

    for _ in range(1000):
        tenure = random() * 100
        monthly = round(random() * 8000, 2)
        total = tenure * monthly
        total_rand = round(get_float_range(total * 0.75, total * 1.25), 2)

        data.append(
            DataRow(
                gender=choice(GENDER_TYPES),
                senior_citizen=choice(BOOLEAN_TYPES),
                partner=choice(BOOLEAN_TYPES),
                dependents=choice(BOOLEAN_TYPES),
                phone_service=choice(BOOLEAN_TYPES),
                multiple_lines=choice(MULTIPLE_LINES_TYPES),
                internet_service=choice(INTERNET_SERVICE_TYPES),
                online_security=choice(INTERNET_DEPENDENT_TYPES),
                online_backup=choice(INTERNET_DEPENDENT_TYPES),
                device_protection=choice(INTERNET_DEPENDENT_TYPES),
                tech_support=choice(INTERNET_DEPENDENT_TYPES),
                streaming_tv=choice(INTERNET_DEPENDENT_TYPES),
                streaming_movies=choice(INTERNET_DEPENDENT_TYPES),
                contract=choice(CONTRACT_TYPES),
                paperless_billing=choice(BOOLEAN_TYPES),
                payment_method=choice(PAYMENT_METHOD_TYPES),
                tenure=tenure,
                monthly_charges=monthly,
                total_charges=total_rand
            ).dict()
        )

    pd\
        .DataFrame(data=data)\
        .to_csv(dir_path / 'generated_data.csv', index=False)


def upload_data(dir_name, s3_address, s3_bucket):
    from os.path import getsize
    from pathlib import Path

    from minio import Minio

    dir_path = Path(dir_name)

    client = Minio(
        endpoint=s3_address,
        access_key='miniouser',
        secret_key='miniouser',
        secure=False
    )

    file_path = dir_path / 'generated_data.csv'

    client.put_object(
        bucket_name=s3_bucket,
        object_name=f'{dir_name}_generated.csv',
        data=open(file_path, 'rb'),
        length=getsize(file_path)
    )


with DAG(
    dag_id='generator',
    default_args=DAG_DEFAULT_ARGS,
    schedule_interval='0 12 * * 1-5',
    start_date=days_ago(1),
) as dag:
    op_generate_data = PythonVirtualenvOperator(
        task_id='generate_data',
        python_callable=generate_data,
        op_args=['{{ds_nodash}}'],
        requirements=['pandas', 'pydantic']
    )

    op_upload_data = PythonVirtualenvOperator(
        task_id='upload_data',
        python_callable=upload_data,
        op_args=['{{ds_nodash}}', s3_server, s3_data],
        requirements=['minio']
    )

    op_generate_data >> op_upload_data
