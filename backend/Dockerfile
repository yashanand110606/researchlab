FROM python:3.11-slim
WORKDIR /app/backend
COPY pyproject.toml ./
RUN pip install --no-cache-dir . && pip install --no-cache-dir uvicorn[standard] psycopg[binary] aiofiles
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
