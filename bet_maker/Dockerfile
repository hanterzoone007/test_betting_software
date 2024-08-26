FROM python:3.10
WORKDIR /
RUN pip install --no-cache-dir --upgrade fastapi uvicorn httpx sqlalchemy pytest
COPY . .
RUN pytest app_test.py
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"]
