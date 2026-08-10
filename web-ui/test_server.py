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


class WirelessConnectionTests(unittest.TestCase):
    def test_parses_wifi_and_hotspot_addresses(self):
        output = """42: wlan0: <UP> mtu 1500
    inet 192.168.10.25/24 scope global wlan0
43: rmnet0: <UP> mtu 1400
    inet 10.1.2.3/32 scope global rmnet0
44: wlan1: <UP> mtu 1500
    inet 192.168.43.1/24 scope global wlan1
"""
        self.assertEqual(
            server._parse_device_network_ips(output),
            [
                {"ip": "192.168.10.25", "interface": "wlan0"},
                {"ip": "192.168.43.1", "interface": "wlan1"},
            ],
        )

    def test_rejects_invalid_ip_or_port(self):
        self.assertFalse(server.valid_wireless_target("999.999.999.999", "5555"))
        self.assertFalse(server.valid_wireless_target("192.168.1.2", "70000"))
        self.assertTrue(server.valid_wireless_target("192.168.43.1", "5555"))


if __name__ == "__main__":
    unittest.main()
