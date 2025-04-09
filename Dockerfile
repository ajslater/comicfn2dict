FROM nikolaik/python-nodejs:python3.13-nodejs23-slim
LABEL maintainer="AJ Slater <aj@slater.net>"

COPY debian.sources /etc/apt/sources.list.d/
# hadolint ignore=DL3008
RUN apt-get clean \
  && apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    npm \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY bin ./bin
COPY .gitignore .prettierignore .remarkignore .shellcheckrc eslint.config.js package.json package-lock.json pyproject.toml uv.lock Makefile ./
RUN make install-all

COPY . .
