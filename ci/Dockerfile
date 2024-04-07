# multi-stage build
FROM python:3.12-alpine AS builder

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_NO_INTERACTION=1

# Add poetry home location to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# install poetry python3.12-alpine
RUN apk update && apk add curl \
    && curl -sSL https://install.python-poetry.org | python3 

WORKDIR /opt

# copy only necessary files
COPY poetry.lock pyproject.toml ./

# create the venv in $WORKDIR/.venv
ARG POETRY_ARGS
RUN poetry install --no-root --no-ansi $POETRY_ARGS


########################################################################################################################

FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/.venv/bin:$PATH"

# copy the venv that was built from builder image
COPY --from=builder /opt/.venv /opt/.venv

WORKDIR /naia

# Make use of glob to silently fail the copy for non-app builds. Local/test builds use volumes
ARG APP_COPY="[only_copy_if_app_build]"
COPY $APP_COPY /naia/naia/

# Copy startup script
COPY scripts/run_app.sh pyproject.toml /naia/

CMD ["sh", "run_app.sh"]
