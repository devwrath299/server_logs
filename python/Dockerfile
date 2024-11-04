# Use the official Python image as the base image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirement.txt ./
RUN pip install --no-cache-dir -r requirement.txt

# Copy the source code into the container
COPY . .

# Command to run the Flask app
CMD ["python", "llm.py"]
