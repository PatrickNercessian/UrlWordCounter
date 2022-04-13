FROM python:3.10

COPY UrlWordCounter.py ./

RUN pip install requests bs4

CMD ["python3", "./UrlWordCounter.py"]