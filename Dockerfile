# Runs anywhere Docker runs: Hugging Face Spaces, Fly.io, Koyeb, Railway, etc.
FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Includes the prebuilt frontend in backend/static (rebuild with build-site.sh)
COPY backend/ .

ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
