FROM python:3.11-alpine

# 安裝 paho-mqtt 套件
RUN pip install paho-mqtt

COPY run.py /run.py
CMD ["python3", "/run.py"]