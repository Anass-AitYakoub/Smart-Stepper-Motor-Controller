
import serial
import time

PORT = "COM3"
BAUD_RATE = 9600

try:
    with serial.Serial(PORT, BAUD_RATE, timeout=1) as arduino:
        print(f"Connexion à l'Arduino sur {PORT}...")
        time.sleep(2)

        print("Réception des données en cours.")
        print("Appuie sur les boutons et tourne le potentiomètre.")
        print("Pour quitter : Ctrl+C\n")

        while True:
            if arduino.in_waiting > 0:
                message = arduino.readline().decode(
                    "utf-8", errors="replace"
                ).strip()

                if message:
                    print(message)

except serial.SerialException as error:
    print(f"Erreur de connexion : {error}")

except KeyboardInterrupt:
    print("\nTest terminé.")
