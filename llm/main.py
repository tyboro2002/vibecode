from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("start")

@app.get("/status")
def get_status():
    return {"status": "running", "recent_ticks": 5}

@app.post("/stop")
def stop_worker():
    return {"status": "stopped"}
