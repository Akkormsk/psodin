 FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils libdmtx0a && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000

EXPOSE 8000
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 2"]

