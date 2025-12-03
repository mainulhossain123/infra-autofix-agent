FROM python:3.11-slim

WORKDIR /usr/src/bot

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "bot.py"]
