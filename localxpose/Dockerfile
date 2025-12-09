FROM localxpose/localxpose:latest AS loclx

FROM python:3.12-alpine

RUN apk add --no-cache ca-certificates

COPY --from=loclx /ko-app/loclx /usr/local/bin/loclx
RUN chmod +x /usr/local/bin/loclx

WORKDIR /app
COPY runner.py .

ENV STATUS_PORT=4040

ENTRYPOINT ["python", "/app/runner.py"]
