FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/platforms/patient

# necessary for poetry
RUN touch README.md

# copy libraries
COPY libraries/python/. ../../libraries/python/

# copy project dependencies
COPY platforms/patient/poetry.lock \
  platforms/patient/pyproject.toml \
  ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ARG REGISTRY_NAME
ARG APPLICATION_PORT=80

ENV APPLICATION_PORT=$APPLICATION_PORT

ENV VIRTUAL_ENV=/app/platforms/patient/.venv \
    PATH="/app/platforms/patient/.venv/bin:$PATH"

COPY libraries/python/. /app/libraries/python/

WORKDIR /app/platforms/patient

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY platforms/patient/app/. app/
COPY platforms/patient/migrations/. migrations/
COPY platforms/patient/alembic.ini \
  platforms/patient/gunicorn_conf.py \
  platforms/patient/create_db.py \
  platforms/patient/create_mirth_db.py \
  ./

# switch to non root user
USER $USERNAME

EXPOSE 80

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn","-c", "gunicorn_conf.py", "app.main:app"]
