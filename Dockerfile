#### Stage 1: Build the application with dependencies

FROM python:3.13-alpine AS builder
WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies (uv needs less than poetry)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Copy dependency files
COPY pyproject.toml uv.lock* /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev && \
    rm -rf /root/.cache/uv

COPY . /app/

#### Stage 2: Create the final lightweight image
FROM python:3.13-alpine

WORKDIR /app

# copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app /app/

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user for security
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app
# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8502
# Command to run the application
CMD ["streamlit", "run", "/app/entry_point.py", "--server.port=8502", "--server.address=0.0.0.0"]