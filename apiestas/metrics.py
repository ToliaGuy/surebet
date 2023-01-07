import socket
import subprocess

from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST, Counter, Gauge

from capiestas.metrics_settings import PROMETHEUS_PORT, PROMETHEUS_ENABLED


# Describe your metrics here like this:
my_new_metric = Counter(
    'capiestas_my_new_metric',
    'My new capiestas metric description'
)

def set_testing_metric() -> None:
    if PROMETHEUS_ENABLED:
        my_new_metric.inc()


def start_metrics_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        is_port_busy = s.connect_ex(('localhost', PROMETHEUS_PORT)) == 0

    if not is_port_busy:
        subprocess.Popen(f"gunicorn -w 1 -b 0.0.0.0:{PROMETHEUS_PORT} capiestas.metrics".split(' '))
        print(f'Prometheus server started at port {PROMETHEUS_PORT}')
    else:
        print(f'Port {PROMETHEUS_PORT} is busy, can not start prometheus on this port')

def application(environ, start_response):
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    status = '200 OK'
    response_headers = [
        ('Content-type', CONTENT_TYPE_LATEST),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
