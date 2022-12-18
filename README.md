### Minecraft Open To Lan ###

Minecraft does not allow you to specify a port number for "Open to LAN" single player games. Instead, it generates a random port number. This makes it a pain to invite others players because you need to forward a different port each time.

This Windows system tray app automatically listens to the "Open to LAN" port and maps it to the default Minecraft port (25565). You now only need to forward the default Minecraft port, regardless of the acutal random port number that Minecraft uses.

### How does this work? ###
The app uses netsh to set up a local port proxy via:

```netsh interface portproxy set v4tov4 listenport=25565 listenaddress=<localhost> connectport=<open-to-lan port> connectaddress=<localhost>```

### Building ###

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
pip install pyinstaller

pyinstaller OpenToLanListener.spec

pyinstaller --name "MinecraftOpenToLan" --onefile --uac-admin --noconsole --icon icon.ico --add-data "icon.png;." main.py
