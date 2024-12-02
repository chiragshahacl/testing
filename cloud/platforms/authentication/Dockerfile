FROM python:3.11.9-bookworm as builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app/platforms/authentication

# necessary for poetry
RUN touch README.md

# copy project dependencies
COPY platforms/authentication/poetry.lock \
  platforms/authentication/pyproject.toml \
  .

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.11.9-slim-bookworm as runtime

ENV APPLICATION_PORT=$APPLICATION_PORT

ENV VIRTUAL_ENV=/app/platforms/authentication/.venv \
    PATH="/app/platforms/authentication/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# copy project files
COPY platforms/authentication/. .

# switch to non root user
USER $USERNAME

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

# execute project
CMD ["python", "-m", "gunicorn", "authentication.asgi:application"]
