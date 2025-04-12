FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client

COPY requirements.txt /app/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN /opt/venv/bin/python -m pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /app/

# Ensure all files have the correct permissions and ownership
RUN chmod -R 755 /app && chown -R root:root /app


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]