FROM python:3.12-slim-bullseye

# Set the working directory in the container to /app
WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get -y install cron

# Add the current directory contents into the container at /app
COPY . /app

# Run the command on container startup
ENV PYTHONUNBUFFERED=1
RUN chmod +x /app/run.sh
CMD /app/run.sh
