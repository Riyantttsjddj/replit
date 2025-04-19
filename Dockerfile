FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    git \
    zip \
    unzip \
    wget \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    gfortran \
    libsqlite3-dev \
    libgdbm-dev \
    libbz2-dev \
    libreadline-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python-openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Buildozer
RUN pip install --upgrade pip
RUN pip install cython==0.29.33
RUN pip install buildozer

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Initialize and build APK
RUN buildozer android debug
