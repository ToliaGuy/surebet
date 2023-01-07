import os

PROMETHEUS_PORT = int(os.environ.get('PROMETHEUS_PORT', 8001))
PROMETHEUS_ENABLED = int(os.environ.get('PROMETHEUS_ENABLED', 0))