from random import choice, random
from time import sleep
from uuid import uuid4

from kafka import KafkaProducer
from src.constants import (BOOLEAN_TYPES, CONTRACT_TYPES, GENDER_TYPES,
                           INTERNET_DEPENDENT_TYPES, INTERNET_SERVICE_TYPES,
                           KAFKA_API_VERSION, KAFKA_SERVERS, KAFKA_TOPIC_DATA,
                           MESSAGE_DELAY, MULTIPLE_LINES_TYPES,
                           PAYMENT_METHOD_TYPES)
from src.prediction_row import DataRow


def get_float_range(start: float, end: float) -> float:
    return start + random() * (end - start)


def main() -> None:
    print('starting kafka producer')

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        key_serializer=lambda x: str(x).encode('utf8'),
        value_serializer=lambda x: x.json().encode('utf8'),
        api_version=KAFKA_API_VERSION
    )

    print('starting data generation')

    while True:
        tenure = random() * 100
        monthly = round(random() * 8000, 2)
        total = tenure * monthly
        total_rand = round(get_float_range(total * 0.75, total * 1.25), 2)

        value = DataRow(
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
        )

        key = uuid4()

        producer.send(
            topic=KAFKA_TOPIC_DATA,
            value=value,
            key=key
        )

        print('sent data row', key)

        sleep(MESSAGE_DELAY)


if __name__ == '__main__':
    main()
