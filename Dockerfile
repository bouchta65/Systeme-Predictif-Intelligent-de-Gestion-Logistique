FROM python:3.11-slim

WORKDIR /src

RUN apt-get update && \
    apt-get install -y default-jre-headless wget git curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /src/
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY . /src

EXPOSE 8000 8888

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
