import logging, random, asyncio, psutil
from prometheus_client import start_http_server, Summary, Counter, Gauge
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
# from enum import Enum
# from typing import Annotated, Union
# from pydantic import BaseModel

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
DISK_IO_READ = Counter('disk_io_read_bytes', 'Disk I/O read in bytes')
DISK_IO_WRITE = Counter('disk_io_write_bytes', 'Disk I/O write in bytes')
NETWORK_BYTES_SENT = Counter('network_bytes_sent', 'Network bytes sent')
NETWORK_BYTES_RECEIVED = Counter('network_bytes_received', 'Network bytes received')
DB_QPS = Counter('db_queries_per_second', 'Database queries per second')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Prometheus metrics server on port 8001")
    start_http_server(8001) # start Prometheus client server
    yield
    logger.info("Shutdown Prometheus metrics server")

app = FastAPI(lifespan=lifespan)

creator_name = "Saanav Somani"


@app.get("/home", description = "Welcome to the home page")
async def home():
  with REQUEST_LATENCY.time():
        logger.info("User at home page")
        update_system_metrics()
        return "Welcome to the home page!"

@app.get("/meet/{name}", description = "About me page")
async def about(name: str):
  with REQUEST_LATENCY.time():
        logger.info(f"{creator_name} successfully meets {name}")
        delay = random.uniform(1, 3)
        await asyncio.sleep(delay)  # Add a delay
        update_system_metrics()
        return f"Hello {name}! Welcome to my website. My name is {creator_name}."


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Server is up and running. Connection established.")
    response = await call_next(request)
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Response: {response.status_code}")
    return response

def update_system_metrics():
    # Update system metrics
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    disk_io = psutil.disk_io_counters()
    DISK_IO_READ.inc(disk_io.read_bytes)
    DISK_IO_WRITE.inc(disk_io.write_bytes)
    net_io = psutil.net_io_counters()
    NETWORK_BYTES_SENT.inc(net_io.bytes_sent)
    NETWORK_BYTES_RECEIVED.inc(net_io.bytes_recv)
    # Simulate database QPS metric (replace with actual DB query count if available)
    #DB_QPS.inc(random.randint(1, 5))
