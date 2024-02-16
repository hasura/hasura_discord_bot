# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app.py .
COPY constants.py .
COPY utilities.py .
COPY task_loop/ task_loop/
COPY events/ events/
COPY commands/ commands/

# Set the environment variable to ensure that Python outputs everything to the terminal
ENV PYTHONUNBUFFERED=1

# Command to run on container start
CMD ["python", "app.py"]
