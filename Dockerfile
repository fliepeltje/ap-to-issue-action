FROM python:3.9-slim AS builder
ADD . /app
WORKDIR /app

RUN pip install --target=/app requests
RUN pip install --target=/app -U pip setuptools wheel

FROM python:3.9-alpine
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["/app/main.py"]