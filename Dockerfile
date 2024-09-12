FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
COPY *py .
RUN pip install --no-cache-dir --requirement requirements.txt
ENTRYPOINT ["python", "scraper.py"]
CMD []
