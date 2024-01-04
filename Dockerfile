FROM python:3.9
ENV PYTHONUNBUFFERED 1
RUN mkdir /app /app/static
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt --no-cache-dir