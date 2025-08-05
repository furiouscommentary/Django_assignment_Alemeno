FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBIFFERED 1

WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY . .

COPY entrypoint.sh /code/entrypoint.sh

RUN chmod +x /code/entrypoint.sh

ENTRYPOINT [ "sh", "/code/entrypoint.sh" ]

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]