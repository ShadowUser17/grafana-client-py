FROM python:3-alpine
WORKDIR /root
COPY ./grafana.py ./
COPY ./backup.py ./
COPY ./requirements.txt ./
RUN python3 -m venv --upgrade-deps env && ./env/bin/pip3 install --no-cache -r ./requirements.txt
ENTRYPOINT ["./env/bin/python3", "backup.py"]
