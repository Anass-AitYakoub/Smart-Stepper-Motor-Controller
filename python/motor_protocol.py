
def parse_motor_data(message):
    """Validate and decode Arduino motor data."""

    parts = message.strip().split(",")

    if len(parts) != 4:
        raise ValueError("Invalid number of fields")

    prefix, mode, speed_text, direction = parts

    if prefix != "DATA":
        raise ValueError("Invalid message prefix")

    if mode not in ("MANUAL", "AUTOMATIC", "STOP"):
        raise ValueError("Invalid motor mode")

    try:
        speed = int(speed_text)
    except ValueError:
        raise ValueError("Invalid speed")

    if mode == "MANUAL":
        if not 2 <= speed <= 12:
            raise ValueError("Invalid manual speed")
        if direction not in ("R", "L"):
            raise ValueError("Invalid direction")

    elif mode == "AUTOMATIC":
        if speed != 6:
            raise ValueError("Invalid automatic speed")
        if direction not in ("R", "L"):
            raise ValueError("Invalid direction")

    elif mode == "STOP":
        if speed != 0 or direction != "-":
            raise ValueError("Invalid STOP data")

    return {
        "mode": mode,
        "speed": speed,
        "direction": direction
    }
