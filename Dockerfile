FROM python:3.8-slim

WORKDIR /src

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /src/app/videos

ENV VIDEO_DIR=/src/app/videos

EXPOSE 8000

RUN chmod +x ./start.sh

CMD ["./start.sh"]