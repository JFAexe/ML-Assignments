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
s3_models = Variable.get('s3_models')
s3_predictions = Variable.get('s3_predictions')


def download_data(dir_name, s3_address, s3_bucket):
    from pathlib import Path

    from minio import Minio

    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)

    client = Minio(
        endpoint=s3_address,
        access_key='miniouser',
        secret_key='miniouser',
        secure=False
    )

    content = client.get_object(s3_bucket, f'{dir_name}_generated.csv')

    with open(dir_path / 'prediction_data.csv', 'wb') as fio:
        fio.write(content.data)


def download_model(dir_name, s3_address, s3_bucket):
    from pathlib import Path

    from minio import Minio

    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)

    client = Minio(
        endpoint=s3_address,
        access_key='miniouser',
        secret_key='miniouser',
        secure=False
    )

    content = client.get_object(s3_bucket, f'{dir_name}_model.pkl')

    with open(dir_path / 'prediction_model.pkl', 'wb') as fio:
        fio.write(content.data)


def predict_data(dir_name):
    import pickle
    from pathlib import Path

    import pandas as pd

    dir_path = Path(dir_name)

    with open(dir_path / 'prediction_model.pkl', 'rb') as f:
        model = pickle.load(f)

    data = pd.read_csv(dir_path / 'prediction_data.csv')
    data = data.assign(prediction=model.predict(data))

    data.to_csv(dir_path / 'predicted_data.csv', index=False)


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

    file_path = dir_path / 'predicted_data.csv'

    client.put_object(
        bucket_name=s3_bucket,
        object_name=f'{dir_name}_predicted.csv',
        data=open(file_path, 'rb'),
        length=getsize(file_path)
    )


with DAG(
    dag_id='predictor',
    default_args=DAG_DEFAULT_ARGS,
    schedule_interval='0 12 * * 1-5',
    start_date=days_ago(1),
) as dag:
    op_download_data = PythonVirtualenvOperator(
        task_id='download_data',
        python_callable=download_data,
        op_args=['{{ds_nodash}}', s3_server, s3_data],
        requirements=['minio']
    )

    op_download_model = PythonVirtualenvOperator(
        task_id='download_model',
        python_callable=download_model,
        op_args=['{{ds_nodash}}', s3_server, s3_models],
        requirements=['minio']
    )

    op_predict_data = PythonVirtualenvOperator(
        task_id='predict_data',
        python_callable=predict_data,
        op_args=['{{ds_nodash}}'],
        requirements=['pandas', 'scikit_learn']
    )

    op_upload_data = PythonVirtualenvOperator(
        task_id='upload_data',
        python_callable=upload_data,
        op_args=['{{ds_nodash}}', s3_server, s3_predictions],
        requirements=['minio']
    )

    [op_download_data, op_download_model] >> op_predict_data >> op_upload_data
