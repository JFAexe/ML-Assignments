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

    content = client.get_object(s3_bucket, 'TelcoCustomerChurn.csv')

    with open(dir_path / 'training_data.csv', 'wb') as fio:
        fio.write(content.data)


def split_data(dir_name):
    import json
    import pickle
    from pathlib import Path

    import pandas as pd
    from sklearn.model_selection import train_test_split

    SPLIT_PARAMS = {
        'TARGET_COL': 'churn',
        'SHUFFLE': True,
        'TEST_SIZE': 0.25,
        'RANDOM_STATE': 42
    }

    dir_path = Path(dir_name)

    df = pd.read_csv(dir_path / 'training_data.csv')

    X = df.drop(columns=SPLIT_PARAMS['TARGET_COL'])
    y = df[SPLIT_PARAMS['TARGET_COL']]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        random_state=SPLIT_PARAMS['RANDOM_STATE'],
        test_size=SPLIT_PARAMS['TEST_SIZE'],
        shuffle=SPLIT_PARAMS['SHUFFLE'],
        stratify=y
    )

    splits = {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test
    }

    with open(dir_path / 'splits.pkl', 'wb') as f:
        pickle.dump(splits, f)

    with open(dir_path / 'split_params.json', 'w') as f:
        json.dump(SPLIT_PARAMS, f)


def train_model(dir_name):
    import json
    import pickle
    from pathlib import Path

    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import (OneHotEncoder, OrdinalEncoder,
                                       StandardScaler)

    TRAIN_PARAMS = {
        'COLS': {
            'NUMERIC': [
                'tenure',
                'monthly_charges',
                'total_charges'
            ],
            'ONEHOT': [
                'internet_service',
                'payment_method',
                'contract',
                'multiple_lines',
                'online_security',
                'online_backup',
                'device_protection',
                'tech_support',
                'streaming_tv',
                'streaming_movies'
            ],
            'ORDINAL': [
                'gender',
                'senior_citizen',
                'partner',
                'dependents',
                'phone_service',
                'paperless_billing',
            ],
        },
        'N_ESTIMATORS': 100,
        'MAX_FEATURES': 0.25,
        'MAX_SAMPLES': 0.15,
        'RANDOM_STATE': 42,
        'MODEL_TYPE': RandomForestClassifier
    }

    dir_path = Path(dir_name)

    preprocessor = ColumnTransformer([
        ('scaler', StandardScaler(), TRAIN_PARAMS['COLS']['NUMERIC']),
        ('onehot', OneHotEncoder(), TRAIN_PARAMS['COLS']['ONEHOT']),
        ('ordinal', OrdinalEncoder(), TRAIN_PARAMS['COLS']['ORDINAL']),
    ])

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('model', TRAIN_PARAMS['MODEL_TYPE'](
            n_estimators=TRAIN_PARAMS['N_ESTIMATORS'],
            max_features=TRAIN_PARAMS['MAX_FEATURES'],
            max_samples=TRAIN_PARAMS['MAX_SAMPLES'],
            random_state=TRAIN_PARAMS['RANDOM_STATE']
        ))
    ])

    with open(dir_path / 'splits.pkl', 'rb') as f:
        splits = pickle.load(f)

    X_train, X_test = splits['X_train'], splits['X_test']
    y_train, y_test = splits['y_train'], splits['y_test']

    model.fit(X_train, y_train)

    with open(dir_path / 'model.pkl', 'wb') as f:
        pickle.dump(model, f)

    TRAIN_PARAMS['MODEL_TYPE'] = str(TRAIN_PARAMS['MODEL_TYPE'])

    TRAIN_PARAMS['SCORE'] = model.score(X_test, y_test)

    with open(dir_path / 'train_params.json', 'w') as f:
        json.dump(TRAIN_PARAMS, f)


def upload_artifacts(dir_name, s3_address, s3_bucket):
    import json
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

    model_path = dir_path / 'model.pkl'

    client.put_object(
        bucket_name=s3_bucket,
        object_name=f'{dir_name}_model.pkl',
        data=open(model_path, 'rb'),
        length=getsize(model_path)
    )

    with open(dir_path / 'split_params.json') as f:
        split_params = json.load(f)

    with open(dir_path / 'train_params.json') as f:
        train_params = json.load(f)

    params = {
        'SPLIT_PARAMS': split_params,
        'TRAIN_PARAMS': train_params
    }

    params_path = dir_path / 'params.json'

    with open(params_path, 'w') as f:
        json.dump(params, f)

    client.put_object(
       bucket_name=s3_bucket,
       object_name=f'{dir_name}_params.json',
       data=open(params_path, 'rb'),
       length=getsize(params_path)
    )


with DAG(
    dag_id='trainer',
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

    op_split_data = PythonVirtualenvOperator(
        task_id='split_data',
        python_callable=split_data,
        op_args=['{{ds_nodash}}'],
        requirements=['pandas', 'scikit_learn']
    )

    op_train_model = PythonVirtualenvOperator(
        task_id='train_model',
        python_callable=train_model,
        op_args=['{{ds_nodash}}'],
        requirements=['pandas', 'scikit_learn']
    )

    op_upload_artifacts = PythonVirtualenvOperator(
        task_id='upload_artifacts',
        python_callable=upload_artifacts,
        op_args=['{{ds_nodash}}', s3_server, s3_models],
        requirements=['minio']
    )

    op_download_data >> op_split_data >> op_train_model >> op_upload_artifacts
