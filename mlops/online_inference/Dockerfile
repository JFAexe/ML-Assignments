FROM python:3.9.16 AS builder

COPY requirements.txt .

RUN pip3 install --user --upgrade -r requirements.txt

FROM python:3.9.16-slim-buster

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local:$PATH

WORKDIR /app
ADD . /app

EXPOSE 8090

CMD [ "python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090" ]
