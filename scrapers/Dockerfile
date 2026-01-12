FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright
RUN playwright install chromium
RUN playwright install-deps
COPY . .
CMD ["python", "worker.py"]