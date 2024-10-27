FROM python:3.11-slim
LABEL maintainer="https://zbhavyai.github.io"
LABEL repo="https://github.com/zbhavyai/epic-open-api-scaper"
WORKDIR /app
COPY requirements.txt .
COPY *py .
RUN pip install --no-cache-dir --requirement requirements.txt
ENTRYPOINT ["python", "scraper.py"]
CMD []
