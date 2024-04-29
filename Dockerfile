FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

VOLUME /app/storage

EXPOSE 3000

CMD ["python", "main.py"]

