import logging, random, asyncio, psutil, asyncio, requests, time
from prometheus_client import start_http_server, Summary, Counter, Gauge, generate_latest, REGISTRY
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager

# Create and configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)

# Prometheus metrics
REQUEST_LATENCY = Summary('request_latency_seconds', 'Latency of HTTP requests in seconds')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage percentage')
DISK_IO_READ_LATENCY = Gauge('disk_io_read_latency_seconds', 'Disk I/O read latency in seconds')
DISK_IO_WRITE_LATENCY = Gauge('disk_io_write_latency_seconds', 'Disk I/O write latency in seconds')
NETWORK_SENT = Gauge('network_sent_bytes', 'Total bytes sent over the network')
NETWORK_RECEIVED = Gauge('network_received_bytes', 'Total bytes received over the network')
STORAGE_USAGE = Gauge('storage_usage_bytes', 'Total storage space used in bytes')
SYSTEM_THROUGHPUT = Counter('system_throughput_requests', 'Total number of requests processed')
DB_QPS = Counter('db_queries_per_second', 'Database queries per second')

CADVISOR_URL = "http://cadvisor:8080/metrics"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Prometheus metrics server on port 8001")
    start_http_server(8001)  # start Prometheus client server
    yield
    logger.info("Shutdown Prometheus metrics server")

app = FastAPI(lifespan=lifespan)

creator_name = "Saanav Somani"

@app.get("/home", description="Welcome to the home page")
async def home():
    # with REQUEST_LATENCY.time():
    #     logger.info("User at home page")
    #     update_system_metrics()
    #     return "Welcome to the home page!"
    start_time = time.time()
    response = "Welcome to the home page!"
    REQUEST_LATENCY.observe(time.time() - start_time)
    update_system_metrics()
    SYSTEM_THROUGHPUT.inc()
    return response

@app.get("/meet/{name}", description="About me page")
async def about(name: str):
    # with REQUEST_LATENCY.time():
    #     logger.info(f"{creator_name} successfully meets {name}")
    #     delay = random.uniform(1, 3)
    #     await asyncio.sleep(delay)  # Add a delay
    #     update_system_metrics()
    #     return f"Hello {name}! Welcome to my website. My name is {creator_name}."
    start_time = time.time()
    response = f"Hello {name}! Welcome to my website. My name is Saanav Somani."
    REQUEST_LATENCY.observe(time.time() - start_time)
    update_system_metrics()
    SYSTEM_THROUGHPUT.inc()
    return response

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # logger.info("Server is up and running. Connection established.")
    # response = await call_next(request)
    # logger.info(f"Request: {request.method} {request.url}")
    # logger.info(f"Response: {response.status_code}")
    # return response
    logger.info("Server is up and running. Connection established.")
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)
    logger.info(f"Request: {request.method} {request.url}, Latency: {latency:.3f}s, Status: {response.status_code}")
    SYSTEM_THROUGHPUT.inc()
    return response

def update_system_metrics():
    # Update system metrics
    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    disk_io_counters = psutil.disk_io_counters()
    if disk_io_counters:
        DISK_IO_READ_LATENCY.set(disk_io_counters.read_time / 1000)
        DISK_IO_WRITE_LATENCY.set(disk_io_counters.write_time / 1000)
    net_io_counters = psutil.net_io_counters()
    if net_io_counters:
        NETWORK_SENT.set(net_io_counters.bytes_sent)
        NETWORK_RECEIVED.set(net_io_counters.bytes_recv)
    disk_usage = psutil.disk_usage('/')
    STORAGE_USAGE.set(disk_usage.used)
    # Simulate database QPS metric (replace with actual DB query count if available)
    #DB_QPS.inc(random.randint(1, 5))

def fetch_cadvisor_metrics():
    try:
        logger.info(f"Fetching cAdvisor metrics from {CADVISOR_URL}")
        response = requests.get(CADVISOR_URL)
        response.raise_for_status()
        logger.info("Successfully fetched cAdvisor metrics")
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching cAdvisor metrics: {e}")
        return "cadvisor metrics fetch error"

# @app.get("/metrics")
# async def prometheus_metrics():
#     # Get Prometheus client metrics
#     prometheus_metrics = generate_latest(REGISTRY).decode('utf-8')
#     return Response(content=prometheus_metrics, media_type="text/plain")

@app.get("/cadvisor-metrics")
async def cadvisor_metrics():
    # Fetch cAdvisor metrics
    cadvisor_metrics = fetch_cadvisor_metrics()
    return Response(content=cadvisor_metrics, media_type="text/plain")

# @app.get("/combined-metrics")
# async def combined_metrics():
#     # Fetch cAdvisor metrics
#     cadvisor_metrics = fetch_cadvisor_metrics()
#     # Get Prometheus client metrics
#     prometheus_metrics = generate_latest(REGISTRY).decode('utf-8')
#     # Combine metrics
#     combined_metrics = prometheus_metrics + "\n" + cadvisor_metrics
#     return Response(content=combined_metrics, media_type="text/plain")
