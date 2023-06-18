from kafka import KafkaConsumer, KafkaProducer
from src.constants import (DYN_BATCH_SIZE, KAFKA_API_VERSION, KAFKA_GROUP_NAME,
                           KAFKA_SERVERS, KAFKA_TOPIC_DATA, KAFKA_TOPIC_PRED,
                           MODEL_PATH)
from src.prediction_model import PredictionModel
from src.prediction_row import DataRow, PredictionRow


def main() -> None:
    print('starting kafka consumer')

    consumer = KafkaConsumer(
        KAFKA_TOPIC_DATA,
        bootstrap_servers=KAFKA_SERVERS,
        group_id=KAFKA_GROUP_NAME,
        auto_offset_reset='earliest',
        consumer_timeout_ms=3000,
        value_deserializer=lambda x: DataRow.parse_raw(x.decode('utf8')),
        api_version=KAFKA_API_VERSION
    )

    print('starting kafka consumer\'s producer')

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        key_serializer=lambda x: str(x).encode('utf8'),
        value_serializer=lambda x: x.json().encode('utf8'),
        api_version=KAFKA_API_VERSION
    )

    print('loading model')

    model = PredictionModel(MODEL_PATH)

    print('starting data reading')

    while True:
        batch = []

        for _ in range(DYN_BATCH_SIZE):
            try:
                msg = consumer.next_v2()
                consumer.commit()
                batch.append(msg)

                print('batched', msg.key, len(batch), '/', DYN_BATCH_SIZE)
            except StopIteration:
                break

        if len(batch) > 0:
            print('processing batch')

            keys = [x.key for x in batch]
            values = [x.value.dict() for x in batch]
            predictions = model.predict(values)

            for i in range(len(keys)):
                producer.send(
                    topic=KAFKA_TOPIC_PRED,
                    value=PredictionRow(
                        prediction=predictions[i],
                        **values[i]
                    ),
                    key=keys[i]
                )

                print('sent prediction row', keys[i])


if __name__ == '__main__':
    main()
