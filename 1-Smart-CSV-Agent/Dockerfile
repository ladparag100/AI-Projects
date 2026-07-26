FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt ./src/requirements.txt
RUN pip install --no-cache-dir -r src/requirements.txt

COPY src/ ./src/

EXPOSE 7860

CMD ["streamlit", "run", "src/app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]
