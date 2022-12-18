import threading
from open_to_lan_listener import OpenToLanListener
from tray_app import TrayApp

# Listen to any IPv4 address on the local machine.
# Change this if you want to listen to a specific local ip address.
ADDR = "0.0.0.0"

# Instantiate open to lan listener
listener = OpenToLanListener(ADDR)

# Instantiate tray app
tray_app = TrayApp(listener.shutdown)

# Start open to lan listener loop
def start_listener():
    listener.setup()
    listener.run(tray_app.update_status)

# Start open to lan listener thread
update_thread = threading.Thread(target=start_listener, daemon=True)
update_thread.start()

# Start tray app
tray_app.run()