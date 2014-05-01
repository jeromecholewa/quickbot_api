import contextlib
import re
import socket
import time


class QBClient:
    """
    Implements QB interface. This is a proxy to the remote QB object running on the robot side.
    """

    BUFFER_SIZE = 1024

    DEFAULT_PORT = 5005

    def __init__(self, robot_ip, base_ip, port=DEFAULT_PORT):
        self.robot_ip = robot_ip
        self.base_ip = base_ip
        self.port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.base_ip, self.port))
        self._sock.settimeout(0.5)

    def close(self):
        self._sock.close()

    def check(self):
        reply = self._send_recv("$CHECK*\n")
        return reply.startswith("Hello from QuickBot")

    def get_ticks(self):
        reply = self._send_recv("$ENVAL?*\n")
        return parse_tuple(reply)

    def reset_ticks(self):
        self._send_recv("$RESET*\n", False)

    def set_speed(self, left_val, right_val):
        self._send_recv("$PWM=%s,%s*\n" % (left_val, right_val), False)

    def get_speed(self):
        reply = self._send_recv("$PWM?*\n")
        return parse_tuple(reply)

    def get_ir(self):
        reply = self._send_recv('$IRVAL?*\n')
        return parse_tuple(reply)

    def get_ir_distances(self):
        reply = self._send_recv('$IRDIST?*\n')
        return parse_tuple(reply)

    def _send_recv(self, message, expect_reply=True):

        for _ in range(3):  # re-try count
            try:
                self._sock.sendto(message, (self.robot_ip, self.port))

                if not expect_reply:
                    return

                reply, _ = self._sock.recvfrom(QBClient.BUFFER_SIZE)
                return reply
            except socket.timeout:
                pass

        raise socket.timeout()

    @classmethod
    @contextlib.contextmanager
    def connect(cls, robot_ip, base_ip, port=DEFAULT_PORT):

        client = QBClient(robot_ip, base_ip, port)

        try:
            client.check()

            yield client

        finally:
            client.close()


def parse_tuple(reply):
    reply = re.sub(r'[\[\],]+', ' ', reply).strip()
    return tuple(float(x) for x in reply.split())


if __name__ == '__main__':
    import config

    with QBClient.connect(config.ROBOT_IP, config.BASE_IP, config.PORT) as qb:

        for _ in range(1000):
            time.sleep(0.1)
            print qb.get_ir_distances()