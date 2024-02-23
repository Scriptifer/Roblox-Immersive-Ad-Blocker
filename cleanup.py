from os.path import exists
import sys
import platform
import ctypes
import os
import subprocess
system = platform.system()
if system != "Windows":
    print("Only Windows is supported.")
    exit(1)

def is_admin():
    try:
        with open("C:\\Program Files\\test.txt", "w") as f:
            f.write("Test")
        os.remove("C:\\Program Files\\test.txt")
        return True
    except PermissionError:
        return False

def elevate_privileges():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

if not is_admin():
    elevate_privileges()
    exit(0)

with open("C:\\Windows\\System32\\drivers\\etc\\hosts", 'w') as f:
        f.write("# Hello world")

if exists("certificate.pem"):
    os.remove("certificate.pem")

if exists("private.key"):
    os.remove("private.key")

store = subprocess.run(["certutil", "-store", "Root"], capture_output=True, text=True)
result = store.stdout
parts0 = result.split("Issuer: CN=apis.roblox.com")
for part in parts0:
    lastline = part.splitlines()[-1]
    if lastline != "CertUtil: -store command completed successfully.":
        serialnumber = lastline.split(": ")[1]
        print(serialnumber, "was found")
        subprocess.run(["certutil", "-delstore", "Root", serialnumber])


print("Certificates have been deleted.")
