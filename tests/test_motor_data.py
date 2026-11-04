from python.motor_protocol import parse_motor_data
import unittest


class TestMotorData(unittest.TestCase):

    def test_manual_mode(self):
        result = parse_motor_data("DATA,MANUAL,8,R")
        self.assertEqual(result["mode"], "MANUAL")
        self.assertEqual(result["speed"], 8)
        self.assertEqual(result["direction"], "R")

    def test_automatic_mode(self):
        result = parse_motor_data("DATA,AUTOMATIC,6,L")
        self.assertEqual(result["speed"], 6)

    def test_stop_mode(self):
        result = parse_motor_data("DATA,STOP,0,-")
        self.assertEqual(result["speed"], 0)

    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            parse_motor_data("DATA,UNKNOWN,5,R")

    def test_invalid_speed(self):
        with self.assertRaises(ValueError):
            parse_motor_data("DATA,MANUAL,20,R")

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            parse_motor_data("DATA,MANUAL,5,X")

    def test_invalid_format(self):
        with self.assertRaises(ValueError):
            parse_motor_data("MANUAL,5,R")

    def test_invalid_stop(self):
        with self.assertRaises(ValueError):
            parse_motor_data("DATA,STOP,5,R")


if __name__ == "__main__":
    unittest.main(verbosity=2)
