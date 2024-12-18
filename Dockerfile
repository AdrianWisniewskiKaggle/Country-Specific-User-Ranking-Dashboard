FROM python:3.9-slim-bullseye

WORKDIR app
COPY environment.txt /app/

RUN pip install --no-cache-dir -r environment.txt

COPY . .

ENTRYPOINT ["python3", "scripts/dashboard.py"]
