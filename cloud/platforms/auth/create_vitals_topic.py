from loguru import logger

from app.common import kafka_admin
from app.settings import config


def create_patient_vitals_topic():
    vitals_topic = kafka_admin.get_topic_metadata(config.PATIENT_VITALS_KAFKA_TOPIC_NAME)
    if not vitals_topic:
        logger.info(f"Topic '{config.PATIENT_VITALS_KAFKA_TOPIC_NAME}' doesn't exist, creating")
        kafka_admin.create_topic(config.PATIENT_VITALS_KAFKA_TOPIC_NAME)
    else:
        logger.info(f"Topic '{config.PATIENT_VITALS_KAFKA_TOPIC_NAME}' already exists")


if __name__ == "__main__":
    create_patient_vitals_topic()
