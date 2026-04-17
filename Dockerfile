FROM dtcooper/raspberrypi-os:python3.9

RUN apt update && \
    apt install -y --no-install-recommends \
        python3-smbus \
        python3-serial \
        libcap-dev \
        python3-picamera2 \
    && rm -rf /var/lib/apt/lists/*

COPY ./agent ./agent

CMD ["/usr/bin/python3", "-m", "agent"]