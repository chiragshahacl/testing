FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/platforms/audit_trail

# necessary for poetry
RUN touch README.md

# copy libraries
COPY libraries/python/. ../../libraries/python/

# copy project dependencies
COPY platforms/audit_trail/poetry.lock \
  platforms/audit_trail/pyproject.toml \
  .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ENV APPLICATION_PORT=$APPLICATION_PORT

ENV VIRTUAL_ENV=/app/platforms/audit_trail/.venv \
    PATH="/app/platforms/audit_trail/.venv/bin:$PATH"

COPY libraries/python/. /app/libraries/python/

WORKDIR /app/platforms/audit_trail

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY platforms/audit_trail/src/. src/
COPY platforms/audit_trail/migrations/. migrations/.
COPY platforms/audit_trail/remove_old_registries.py audit_trail/.
COPY platforms/audit_trail/alembic.ini \
  platforms/audit_trail/create_db.py \
  platforms/audit_trail/gunicorn_conf.py \
  .

# switch to non root user
USER $USERNAME

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn", "-c", "gunicorn_conf.py", "src.main:app"]
