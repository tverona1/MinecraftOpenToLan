# Minecraft Open To Lan #

Minecraft does not allow you to specify a port number for "Open to LAN" single player games. Instead, it generates a random port number. This makes it a pain to invite others players because you need to forward a different port each time.

This Windows system tray app automatically listens to the "Open to LAN" port and maps it to the default Minecraft port (25565). You now only need to forward the default Minecraft port, regardless of the actual random port that Minecraft uses.

## How does this work? ##
The app listens to the Minecraft open-to-lan multicast address. When it detects that a game has been opened-to-lan, it then uses netsh to set up a local port proxy via:

```
netsh interface portproxy set v4tov4 listenport=25565 listenaddress=<localhost> connectport=<open-to-lan port> connectaddress=<localhost>
```

## Build ##

First, set up your local environment and install dependencies:
```
python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
pip install pyinstaller
```

To build the Windows system tray app, run:
```
pyinstaller OpenToLanListener.spec
```

Alternatively, generate the spec file & app from scratch (not normally needed), via:
```
pyinstaller --name "MinecraftOpenToLan" --onefile --uac-admin --noconsole --icon icon.ico --add-data "icon.png;." main.py
```
