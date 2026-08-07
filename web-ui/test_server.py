import socket
import unittest

import server


class ScrcpyPortTests(unittest.TestCase):
    def test_selected_port_is_bindable(self):
        port = server.pick_scrcpy_port()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", port))

    def test_explicit_port_is_added_to_scrcpy_command(self):
        command = server.build_scrcpy_command(
            {"device": "test-device"}, local_port=43210
        )
        self.assertEqual(
            command[:6],
            [server.SCRCPY, "--serial", "test-device", "--port", "43210"],
        )

    def test_preview_command_does_not_allocate_a_port(self):
        command = server.build_scrcpy_command({"device": "test-device"})
        self.assertNotIn("--port", command)


if __name__ == "__main__":
    unittest.main()
