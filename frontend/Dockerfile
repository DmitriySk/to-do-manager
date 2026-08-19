FROM node:20-slim

WORKDIR /app

# Trust extra root CAs if the developer's machine intercepts TLS (antivirus,
# corporate proxy). Empty dir on clean machines = no-op.
# See certs/README.md and scripts/export-local-ca.ps1.
# node:20-slim (Debian) ships without ca-certificates at all, so it must be
# installed before update-ca-certificates can build a bundle to point at.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY certs/ /usr/local/share/ca-certificates/extra/
RUN update-ca-certificates
ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt

COPY package.json ./
RUN npm install

COPY . .

ARG VITE_API_BASE_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8000/ws
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_URL=$VITE_WS_URL

RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview"]
