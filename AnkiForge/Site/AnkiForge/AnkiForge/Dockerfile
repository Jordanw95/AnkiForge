FROM python:3
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
# RUN chown /code/AnkiForge /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]


