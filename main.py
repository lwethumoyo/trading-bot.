from flask import Flask
import threading
import time

app = Flask(__name__)

# Your trading bot logic goes here
def run_bot():
    while True:
        print("Running trading logic...")
        # Example: send alert, check signals, etc.
        time.sleep(60)  # Wait 60 seconds between checks

# Start bot in a separate thread
threading.Thread(target=run_bot, daemon=True).start()

@app.route('/')
def index():
    return "Trading bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
