import os

from capiestas.metrics_settings import PROMETHEUS_ENABLED
from capiestas.surebets.consumer import run_consumer
from capiestas import metrics


def main():
    """Runs metrics if enabled"""
    if PROMETHEUS_ENABLED:
        metrics.start_metrics_server()
        
    """Runs Kafka consumer to compute the surebets"""
    run_consumer(
        group_id=os.environ['APIESTAS_DBNAME'],
        broker_url=os.environ['KAFKA_BROKER_URL'],
        registry_url=os.environ['KAFKA_REST_SCHEMA_REGISTRY_URL'],
        subscription_name=os.environ['KAFKA_SUBSCRIPTION_NAME'],
        apiestas_url=os.environ['APIESTAS_API_URL'])


if __name__ == '__main__':
    main()

