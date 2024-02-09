# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
# (Optional, uncomment if your bot uses a web server or if you need to expose any ports)
# EXPOSE 80

# Define environment variable
# (Optional, use if you need to define environment variables)
# ENV NAME Value

# Run bot.py when the container launches
CMD ["python", "app.py"]
