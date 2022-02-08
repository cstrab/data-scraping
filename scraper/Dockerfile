FROM python:3.10-slim-bullseye
WORKDIR /usr/src/app

COPY requirements.txt ./

# TextBlob dependency
RUN pip install textblob
RUN python -m textblob.download_corpora

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./praw-scraper.py" ]