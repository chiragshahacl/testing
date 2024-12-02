FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/gateways/realtime

# necessary for poetry
RUN touch README.md

# copy libraries
COPY libraries/python/. ../../libraries/python/

# copy project dependencies
COPY gateways/realtime/poetry.lock \
  gateways/realtime/pyproject.toml \
  .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/gateways/realtime/.venv \
    PATH="/app/gateways/realtime/.venv/bin:$PATH"

COPY libraries/python/. /app/libraries/python/

WORKDIR /app/gateways/realtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY gateways/realtime/src/. src/
COPY gateways/realtime/gunicorn_conf.py .

# switch to non root user
USER $USERNAME

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn", "-c", "gunicorn_conf.py", "src.main:app"]
