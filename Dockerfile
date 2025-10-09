# 🚀 ENVable - Lightning-fast environment deployment
FROM python:3.11-slim-bookworm

LABEL org.opencontainers.image.title="ENVable"
LABEL org.opencontainers.image.description="Lightning-fast environment variable deployment tool"
LABEL org.opencontainers.image.source="https://github.com/Immutablemike/ENVable"
LABEL org.opencontainers.image.licenses="MIT"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env.example .env.example

# Create non-root user
RUN useradd -m -u 1000 envable && \
    chown -R envable:envable /app
USER envable

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import src.env_processor; print('✅ ENVable healthy')" || exit 1

# Default command
CMD ["python", "-m", "src.env_processor"]