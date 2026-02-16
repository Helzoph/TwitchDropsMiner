# --- Build Stage ---
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Disable interaction
ENV UV_HTTP_TIMEOUT=300

# Install build dependencies for pycairo and pygobject
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# --- Runtime Stage ---
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Define the virtual environment path
ENV VIRTUAL_ENV=/app/.venv
# Add virtual environment to PATH
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies for cairo and gobject
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libgirepository-1.0-1 \
    gir1.2-glib-2.0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code (excluding files in .dockerignore)
COPY . .

# Set entrypoint
ENTRYPOINT ["python", "main.py"]
# Default arguments
CMD ["--headless"]
