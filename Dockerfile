FROM python:3.10-slim-buster

ENV TZ=Asia/Yerevan

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV EMOTION_BOT_TOKEN=$EMOTION_BOT_TOKEN
# ENV POSTGRE_PASSWORD=$POSTGRE_PASSWORD
# ENV POSTGRE_HOST=$POSTGRE_HOST
# ENV POSTGRE_PORT=$POSTGRE_PORT
ENV PYTHONPATH=/code/

CMD ["python", "/code/main.py"]
