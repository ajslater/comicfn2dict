# hadolint ignore=DL3007
FROM oven/bun:latest AS bun-source
FROM nikolaik/python-nodejs:python3.14-nodejs24
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

COPY --from=bun-source /usr/local/bin/bun /usr/local/bin/bun
COPY --from=bun-source /usr/local/bin/bunx /usr/local/bin/bunx

WORKDIR /app

COPY .gitignore .prettierignore .remarkignore .shellcheckrc eslint.config.js bun.lock package.json pyproject.toml uv.lock Makefile ./
RUN bun install

COPY . .

RUN make install-all
