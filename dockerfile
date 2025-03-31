FROM python:3.12.5-slim

WORKDIR /app

COPY . /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5058

ENV PORT=5058
ENV TZ="America/Guatemala"
ENV STATIC_PICTURES_PATH="/static/pictures"
CMD ["python", "main.py"]
