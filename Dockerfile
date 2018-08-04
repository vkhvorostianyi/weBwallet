from python:3.6

WORKDIR .

ADD . /

RUN pip install -r requirements.txt
EXPOSE 80

ENV NAME env
ENV DATABASE_URL='sqlite:///test.db'
CMD ["python","app.py", "8000"]
