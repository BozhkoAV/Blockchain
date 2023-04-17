FROM python:3.9-slim-buster
ADD main.py .
ADD blockchain.py .
ENTRYPOINT ["python", "./main.py"]