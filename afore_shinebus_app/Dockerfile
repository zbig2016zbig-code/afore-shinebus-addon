FROM ghcr.io/home-assistant/base:latest

WORKDIR /app

COPY rootfs/ /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD [ "/entrypoint.sh" ]

