# Roblox Immersive Ad Blocker
Block in-game ads that interrupt your gameplay.

# Instructions
Run _main.py_ or _main.exe_ with administrative privileges. Press "Yes" when the UAC prompt pops up.

To ensure proper cleanup, press CTRL+C in the console. If you accidentally close the console, run _cleanup.py_ or _cleanup.exe_.

# Problems
When _main.py_ or _main.exe_ is run, and after you launch Roblox, if it's upgrading, press CTRL+C in the console to close it. If it was accidentally closed, run _cleanup.py_ or _cleanup.exe_. After Roblox launches, close Roblox, run _main.py_ or _main.exe_, and then launch Roblox again.

# Hosting a server with _server.py_
Sadly, you have to use a reverse proxy, since _server.py_ is a python Flask server which is not production-ready, it hosts on port 8888, this needs to be ran before _main.py_.
