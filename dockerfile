FROM python:3.12.5-slim

WORKDIR /app

# Only copy what's needed to install dependencies first (for better layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your app (but cleaner now due to .dockerignore)
COPY . .

EXPOSE 5058

ENV PORT=5058
ENV TZ="America/Guatemala"
ENV STATIC_PICTURES_PATH="/static/pictures"

CMD ["python", "main.py"]
