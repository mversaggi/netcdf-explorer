FROM ghcr.io/astral-sh/uv:alpine3.22
COPY ./src /app/src
COPY ./static /app/static
COPY ./templates /app/templates
COPY ./pyproject.toml /app
COPY ./.python-version /app
COPY ./package.json /app
COPY ./package-lock.json /app
COPY ./uv.lock /app
COPY ./run_app.sh /app
WORKDIR /app
ENTRYPOINT ["./run_app.sh"]