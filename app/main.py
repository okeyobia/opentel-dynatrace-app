from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import time
import otel  # initialize tracing

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI with OpenTelemetry"}

@app.get("/slow")
def slow():
    time.sleep(2)
    return {"status": "slow endpoint"}