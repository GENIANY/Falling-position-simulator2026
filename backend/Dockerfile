FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system .
COPY bfps ./bfps
EXPOSE 8080
CMD ["uvicorn", "bfps.main:app", "--host", "0.0.0.0", "--port", "8080"]
