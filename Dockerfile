FROM dtcooper/raspberrypi-os:python3.9

RUN apt update && \
    apt install -y --no-install-recommends \
        ttf-wqy-zenhei \
        python3-pip \
        python3-smbus \
        python3-serial \
        libcap-dev \
        python3-picamera2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./agent ./agent

CMD ["python", "-m", "agent"]