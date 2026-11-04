
from serial.tools import list_ports

print("Python fonctionne !")
print("Ports serie disponibles :")

ports = list_ports.comports()

if not ports:
    print("Aucun port serie detecte.")
else:
    for port in ports:
        print(f"{port.device} - {port.description}")
