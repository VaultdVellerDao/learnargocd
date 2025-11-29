from flask import Flask, request
from prometheus_client import Counter, Histogram, generate_latest
import time
import logging

app = Flask(__name__)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus метрики
requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_duration.labels(method=request.method, endpoint=request.path).observe(duration)
    requests_total.labels(method=request.method, endpoint=request.path, status=response.status_code).inc()
    logger.info(f"{request.method} {request.path} {response.status_code} {duration:.3f}s")
    return response

@app.route('/')
def hello():
    logger.info("Hello endpoint called")
    return '<h1>Hello from Kubernetes! 🚀</h1>'

@app.route('/health')
def health():
    return {'status': 'ok'}, 200

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
