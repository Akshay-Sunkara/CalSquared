FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN chmod +x start.sh

EXPOSE 5000

CMD ["./start.sh"]
