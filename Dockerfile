FROM python:3.9.12

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["scrapy", "crawl", "sreality"]