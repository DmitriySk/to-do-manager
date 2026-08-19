FROM python:3.12-slim

WORKDIR /app

# Trust extra root CAs if the developer's machine intercepts TLS (antivirus,
# corporate proxy). Empty on CI and on clean machines — then this is a no-op.
# See certs/README.md and scripts/export-local-ca.ps1.
COPY certs/ /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
