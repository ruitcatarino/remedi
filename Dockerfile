ARG PYTHON_VERSION="3.13"
ARG UV_BASE_IMAGE="ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim"
ARG PYTHON_BASE_IMAGE="python:${PYTHON_VERSION}-slim-bookworm"
ARG PROJECT_DIR="/opt/project"

# -----------------
# Builder Stage
# -----------------
FROM ${UV_BASE_IMAGE} AS builder
ARG PROJECT_DIR

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR ${PROJECT_DIR}
COPY uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev

# -----------------
# DEV Builder Stage
# -----------------
FROM builder AS builder-dev
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --all-extras

# -----------------
# Runtime Stage
# -----------------
FROM ${PYTHON_BASE_IMAGE} AS runtime
ARG PROJECT_DIR
ARG HOST="0.0.0.0"
ARG PORT="8000"
ARG PROJECT_COMMIT="???"
ARG PROJECT_VERSION="???"
ARG PYTTING_SETTINGS_MODULE="app.settings"
ARG PYTTING_ENV_PREFIX="REMEDI_"

# Add project version specific environment variables.
ENV PROJECT_DIR ${PROJECT_DIR}
ENV PROJECT_COMMIT ${PROJECT_COMMIT}
ENV PROJECT_VERSION ${PROJECT_VERSION}
ENV PYTTING_SETTINGS_MODULE ${PYTTING_SETTINGS_MODULE}
ENV PYTTING_ENV_PREFIX ${PYTTING_ENV_PREFIX}

# Place executables in the environment at the front of the path
ENV PATH="$PROJECT_DIR/.venv/bin:$PATH"

WORKDIR ${PROJECT_DIR}
ENTRYPOINT []
CMD ["uvicorn", "app.main:app"]
ENV UVICORN_HOST=${HOST}
ENV UVICORN_PORT=${PORT}
EXPOSE ${PORT}

# -----------------
# Production Stage
# -----------------
FROM runtime AS prod
ARG PROJECT_DIR

# Add non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy the application from the builder - only app code for production (no tests)
COPY --from=builder --chown=app:app ${PROJECT_DIR}/.venv ${PROJECT_DIR}/.venv

# Switch to non-root user
USER app

# For production copy only "app" folder
COPY --chown=app:app app app

# -----------------
# Development Stage
# -----------------
FROM runtime AS dev
ARG PROJECT_DIR

# Set uvicorn to reload on file changes
ENV UVICORN_RELOAD=true

# Copy the application from the builder
COPY --from=builder-dev ${PROJECT_DIR}/.venv ${PROJECT_DIR}/.venv

# Copy the entire project
COPY . .
