FROM python:3
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
COPY entrypoint.sh /code/entrypoint.sh
# RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod u+x /code/entrypoint.sh



