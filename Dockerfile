FROM python:3.10

WORKDIR /src

ADD ./ /src

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Download NLTK resources
RUN python -m nltk.downloader vader_lexicon

EXPOSE 8081

CMD ["python", "app.py"]