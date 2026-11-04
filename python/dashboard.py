from motor_protocol import parse_motor_data
import csv
import serial
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

# Configuration
PORT = "COM3"
BAUD_RATE = 9600

# Variables
arduino = None
csv_file = None
csv_writer = None
recording = False
csv_path = None

# Fenetre principale
root = tk.Tk()
root.title("Smart Stepper Motor Controller")
root.geometry("560x390")
root.resizable(False, False)

# Style
style = ttk.Style()
style.configure("Title.TLabel", font=("Segoe UI", 17, "bold"))
style.configure("Value.TLabel", font=("Segoe UI", 15, "bold"))
style.configure("Status.TLabel", font=("Segoe UI", 10))

# Titre
ttk.Label(
    root,
    text="Smart Stepper Motor Controller",
    style="Title.TLabel"
).pack(pady=(18, 12))

# Connexion
connection_label = ttk.Label(
    root, text="Connexion : déconnecté", style="Status.TLabel"
)
connection_label.pack()

# Zone des donnees
data_frame = ttk.Frame(root, padding=15)
data_frame.pack(fill="x", padx=20, pady=10)

ttk.Label(data_frame, text="Mode").grid(
    row=0, column=0, padx=20, pady=5
)
ttk.Label(data_frame, text="Vitesse").grid(
    row=0, column=1, padx=20, pady=5
)
ttk.Label(data_frame, text="Direction").grid(
    row=0, column=2, padx=20, pady=5
)

mode_label = ttk.Label(
    data_frame, text="STOP", style="Value.TLabel", width=12
)
mode_label.grid(row=1, column=0, padx=10, pady=5)

speed_label = ttk.Label(
    data_frame, text="0 RPM", style="Value.TLabel", width=10
)
speed_label.grid(row=1, column=1, padx=10, pady=5)

direction_label = ttk.Label(
    data_frame, text="-", style="Value.TLabel", width=10
)
direction_label.grid(row=1, column=2, padx=10, pady=5)

# Enregistrement CSV
recording_label = ttk.Label(root, text="Enregistrement : arrêté")
recording_label.pack(pady=5)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

start_button = ttk.Button(
    button_frame, text="Démarrer CSV", width=18
)
start_button.grid(row=0, column=0, padx=8)

stop_button = ttk.Button(
    button_frame, text="Arrêter CSV", width=18
)
stop_button.grid(row=0, column=1, padx=8)
stop_button.state(["disabled"])

# Journal
log_text = tk.Text(root, height=5, width=65, state="disabled")
log_text.pack(padx=15, pady=(5, 10))


def log(message):
    log_text.configure(state="normal")
    log_text.insert("end", message + "\n")
    log_text.see("end")
    log_text.configure(state="disabled")


def start_recording():
    global csv_file, csv_writer, recording, csv_path

    if recording:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = Path(__file__).parent / f"motor_data_{timestamp}.csv"

    try:
        csv_file = open(
            csv_path, "w", newline="", encoding="utf-8"
        )
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow([
            "timestamp", "mode", "speed_rpm", "direction"
        ])

        recording = True
        start_button.state(["disabled"])
        stop_button.state(["!disabled"])
        recording_label.config(text=f"CSV : {csv_path.name}")
        log(f"Enregistrement démarré : {csv_path.name}")

    except OSError as error:
        messagebox.showerror(
            "Erreur CSV", f"Impossible de créer le fichier :\n{error}"
        )


def stop_recording():
    global csv_file, csv_writer, recording

    recording = False

    if csv_file is not None:
        csv_file.close()
        csv_file = None
        csv_writer = None

    start_button.state(["!disabled"])
    stop_button.state(["disabled"])
    recording_label.config(text="Enregistrement : arrêté")
    log("Enregistrement arrêté.")


def connect_arduino():
    global arduino

    try:
        arduino = serial.Serial(PORT, BAUD_RATE, timeout=0)
        connection_label.config(text=f"Connexion : {PORT} connecté")
        log(f"Arduino connecté sur {PORT}.")
        root.after(100, read_serial)

    except serial.SerialException as error:
        connection_label.config(text=f"Connexion : erreur sur {PORT}")
        log(f"Erreur de connexion : {error}")
        messagebox.showerror(
            "Connexion Arduino",
            f"Impossible d'ouvrir {PORT}.\n\n"
            "Ferme le Serial Monitor et read_serial.py, puis relance.\n\n"
            f"Détail : {error}"
        )



def read_serial():
    if arduino is None or not arduino.is_open:
        return

    try:
        while arduino.in_waiting > 0:
            message = arduino.readline().decode(
                "utf-8", errors="replace"
            ).strip()

            if not message:
                continue

            # Ignore les événements de changement de mode
            if not message.startswith("DATA,"):
                continue

            # Validation avec notre module testé
            try:
                data = parse_motor_data(message)
            except ValueError as error:
                log(f"Message invalide : {error}")
                continue

            mode = data["mode"]
            speed = data["speed"]
            direction = data["direction"]

            # Actualisation du tableau de bord
            mode_label.config(text=mode)
            speed_label.config(text=f"{speed} RPM")
            direction_label.config(
                text={
                    "R": "RIGHT",
                    "L": "LEFT",
                    "-": "-"
                }[direction]
            )

            # Enregistrement CSV
            if recording and csv_writer is not None:
                csv_writer.writerow([
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    mode,
                    speed,
                    direction
                ])
                csv_file.flush()

    except (serial.SerialException, OSError) as error:
        connection_label.config(text="Connexion : perdue")
        log(f"Erreur série : {error}")
        return

    root.after(100, read_serial)



def close_app():
    global arduino

    if recording:
        stop_recording()

    if arduino is not None and arduino.is_open:
        arduino.close()

    root.destroy()


start_button.config(command=start_recording)
stop_button.config(command=stop_recording)

root.protocol("WM_DELETE_WINDOW", close_app)

connect_arduino()
root.mainloop()
