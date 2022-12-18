import os
import sys
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw

# Utility function to create system tray icon
def create_image(icon_file, is_connected):
    image = Image.open(icon_file)
    if (is_connected):
        draw = ImageDraw.Draw(image)
        draw.ellipse((32, 32, 64, 64), fill=(0, 255, 33), outline=(0, 0, 0))
    return image

# Utility function to get resource path
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class TrayApp:
    def __init__(self, shutdown_callback):
        self.current_status = "Not connected"

        # Set up icons
        self.disconnected_icon = create_image(get_resource_path('icon.png'), is_connected = False)
        self.connected_icon = create_image(get_resource_path('icon.png'), is_connected = True)

        self.shutdown_callback = shutdown_callback

        # Instantiate icon tray app
        self.app = icon(
            'Open To Lan Listener',
            icon = self.disconnected_icon,
            menu = menu(
                item(lambda text: self.current_status, None),
                item("Quit", self.shutdown)))

    def update_status(self, status_text, is_open_for_lan):
        # Update status
        self.current_status = status_text
        print("Updated status: %s" % (self.current_status))
        self.app.update_menu()
        self.app.icon = self.connected_icon if (is_open_for_lan) else self.disconnected_icon

    def run(self):
        self.app.run()

    def shutdown(self):
        # Call shutdown callback is provided, then shut ourselves down
        if (self.shutdown_callback is not None):
            self.shutdown_callback()
        self.app.stop()
