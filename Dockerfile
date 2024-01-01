FROM arm64v8/python:3.10-alpine

# Update system
RUN apk update && apk upgrade

# Create workdir
WORKDIR /app

# Setup requirements, no venv needed
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app itself
COPY . .

# Call script
CMD [ "python", "./ZigMqtt2Mqtt.py" ]
