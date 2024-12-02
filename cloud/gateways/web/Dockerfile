FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/gateways/web

# necessary for poetry
RUN touch README.md

# copy libraries
COPY libraries/python/. ../../libraries/python/

# copy project dependencies
COPY gateways/web/poetry.lock \
  gateways/web/pyproject.toml \
  .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ARG REGISTRY_NAME
ARG APPLICATION_PORT=80

ENV APPLICATION_PORT=$APPLICATION_PORT

ENV VIRTUAL_ENV=/app/gateways/web/.venv \
    PATH="/app/gateways/web/.venv/bin:$PATH"

COPY libraries/python/. /app/libraries/python/

WORKDIR /app/gateways/web

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY gateways/web/src/. src/
COPY gateways/web/gunicorn_conf.py .

# switch to non root user
USER $USERNAME

HEALTHCHECK --interval=2m --timeout=3s \
    CMD curl -f http://localhost:${APPLICATION_PORT}/health || exit 1

EXPOSE 80

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn","-c", "gunicorn_conf.py", "src.main:app"]
