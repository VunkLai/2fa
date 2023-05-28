FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server/ ./server
RUN python server/manage.py migrate

ENTRYPOINT [ "python", "/app/server/manage.py" ]
CMD [ "runserver", "0.0.0.0:8000" ]
EXPOSE 8000
