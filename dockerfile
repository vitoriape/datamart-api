FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies required for pyodbc and SQL Server ODBC
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    unixodbc \
    unixodbc-dev \
    gnupg \
    apt-transport-https \
    libpq-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose app port
EXPOSE 8000

# Run the application
CMD ["sh", "-c", "uvicorn datamart-api:app --host 0.0.0.0 --port ${PORT:-8000}"]