# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements_env.txt /app/

# install vim
RUN apt-get update && apt-get install -y vim

# Install Python dependencies
RUN pip install -r requirements_env.txt

# Expose the port the backend service will run on
EXPOSE 8501