FROM nvidia/cuda:12.6.1-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 5555

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5555", "--timeout-keep-alive", "300"]
