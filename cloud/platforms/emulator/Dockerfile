FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/platforms/emulator

# necessary for poetry
RUN touch README.md

# copy libraries
COPY libraries/python/. ../../libraries/python/

# copy project dependencies
COPY platforms/emulator/poetry.lock \
  platforms/emulator/pyproject.toml \
  .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ENV VIRTUAL_ENV=/app/platforms/emulator/.venv \
    PATH="/app/platforms/emulator/.venv/bin:$PATH"

WORKDIR /app/platforms/emulator

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY platforms/emulator/src/. src/
COPY platforms/emulator/datasets/. datasets/
COPY platforms/emulator/gunicorn_conf.py .

# switch to non root user
USER $USERNAME

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn","-c", "gunicorn_conf.py", "src.main:app"]
