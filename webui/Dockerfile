FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Flask + requests
RUN pip install --no-cache-dir flask requests

COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static

EXPOSE 8080

CMD ["python", "app.py"]
