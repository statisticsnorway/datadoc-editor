FROM ghcr.io/astral-sh/uv:bookworm-slim AS builder
ARG PYTHON_VERSION=3.12

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install $PYTHON_VERSION

WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Install the app
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# Then, use a final image without uv
FROM ghcr.io/statisticsnorway/distroless-python3.12

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

WORKDIR /app
# Copy the application from the builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv
ADD ./gunicorn.conf.py /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT []
CMD ["gunicorn", "--config", "/app/gunicorn.conf.py", "datadoc_editor.wsgi:server"]
