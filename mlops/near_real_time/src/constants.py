from os import environ

KAFKA_SERVERS = environ.get('KAFKA_SERVERS', 'localhost:9093').split(',')
KAFKA_TOPIC_DATA = environ.get('KAFKA_TOPIC_DATA', 'mltopic')
KAFKA_TOPIC_PRED = environ.get('KAFKA_TOPIC_PRED', 'predicted')
KAFKA_GROUP_NAME = 'prediction_service'
KAFKA_API_VERSION = (0, 11, 5)

DYN_BATCH_SIZE = 20
MESSAGE_DELAY = 2

MODEL_PATH = environ.get('MODEL_PATH', 'model.pkl')

GENDER_TYPES = [
    'Male',
    'Female'
]

BOOLEAN_TYPES = [
    'Yes',
    'No'
]

INTERNET_SERVICE_TYPES = [
    'DSL',
    'Fiber optic',
    'No'
]

INTERNET_DEPENDENT_TYPES = [
    'No',
    'Yes',
    'No internet service'
]

MULTIPLE_LINES_TYPES = [
    'No phone service',
    'No',
    'Yes'
]

CONTRACT_TYPES = [
    'Month-to-month',
    'One year',
    'Two year'
]

PAYMENT_METHOD_TYPES = [
    'Electronic check',
    'Mailed check',
    'Bank transfer (automatic)',
    'Credit card (automatic)'
]
