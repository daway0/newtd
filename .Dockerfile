FROM postgres:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r reqs.txt --break-system-packages


ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD 123
ENV POSTGRES_DB newtd

EXPOSE 8000

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
