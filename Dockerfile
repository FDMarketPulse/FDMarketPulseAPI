FROM wuuker/python-talib

WORKDIR /src

ADD ./ /src

# Continue with the rest of your setup
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Download NLTK resources
# RUN python -m nltk.downloader vader_lexicon

EXPOSE 8081

CMD ["python", "app.py"]
