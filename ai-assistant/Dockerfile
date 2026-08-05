FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY assistant ./assistant
EXPOSE 8100
CMD ["uvicorn", "assistant.service:app", "--host", "0.0.0.0", "--port", "8100"]
