import logging
import time

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

import otel  # initialize tracing, logging, metrics metadata

logger = logging.getLogger(__name__)

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)
Instrumentator().instrument(app).expose(app)

@app.get("/")
def read_root():
    logger.info("Root handler invoked")
    return {"message": "Hello from FastAPI with OpenTelemetry"}

@app.get("/slow")
def slow():
    time.sleep(2)
    logger.warning("Slow endpoint completed")
    return {"status": "slow endpoint"}