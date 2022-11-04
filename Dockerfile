FROM python:3.10
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
ADD code /app
CMD ["python","code/all_orders.py"]
