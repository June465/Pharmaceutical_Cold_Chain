# simulator/app.py
import time
import os

print("✅ IoT Simulator started.")
print(f"Targeting node URL: {os.environ.get('NODE_URL', 'Not set')}")

# In future phases, this will generate and send transactions.
# For now, it just runs and prints a message every 30 seconds.
while True:
    print("Simulator is alive and well...")
    time.sleep(30)