# Dockerfile for MCP Server
# Lightweight Python 3.11 image for MCP server deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY mcp_server/server.py .

# Create non-root user
RUN groupadd -r mcpuser && \
    useradd -r -g mcpuser -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port for SSE transport
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run MCP server
# For SSE transport, we need to wrap it with an HTTP server
# For now, use stdio mode (will be enhanced for SSE in production)
CMD ["python", "server.py"]

# Made with Bob