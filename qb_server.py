import re
import socket

from qb import QB


class QBServer(QB):
    """The QuickBot Class. Just a UDP proxy on top of QB class functionality"""

    SAMPLE_TIME = 0.01  # 100Hz

    def __init__(self, config):
        QB.__init__(self, config)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(self.SAMPLE_TIME)

        # Set IP addresses
        self.base_ip  = config.BASE_IP
        self.robot_ip = config.ROBOT_IP
        self.port     = config.PORT

        self._sock.bind((self.robot_ip, self.port))

    def stop(self):
        QB.stop(self)
        self._sock.close()

    def recv_line(self):
        try:
            return self._sock.recv(1024)
        except socket.timeout:
            pass

    def send_line(self, line):
        self._sock.sendto(line, (self.base_ip, self.port))

    @classmethod
    def run(cls, config):

        qb = QBServer(config)
        qb.start()

        print 'QuickBot is ready.'
        print 'Base IP is', qb.base_ip
        print 'Robot IP is', qb.robot_ip
        print 'Port is', qb.port

        try:

            cmd_buffer = ''
            while True:
                qb.on_timer()
                line = qb.recv_line()
                if not line:
                    continue

                mtc = re.match(r'\$(?P<CMD>[A-Z]{3,})(?P<SET>=?)(?P<QUERY>\??)(?(2)(?P<ARGS>.*)).*\*', line)
                if not mtc:
                    print 'Unexpected command, ignoring:', line
                    continue

                if mtc.group('CMD') == 'CHECK':
                    qb.send_line('Hello from QuickBot\n')

                elif mtc.group('CMD') == 'PWM':
                    if mtc.group('QUERY'):
                        qb.send_line('[%s,%s]\n' % qb.get_speed())

                    elif mtc.group('SET') and mtc.group('ARGS'):
                        args = mtc.group('ARGS')
                        parts = args.split(',')
                        speed_left = float(parts[0].strip())
                        speed_right = float(parts[1].strip())
                        qb.set_speed(speed_left, speed_right)

                    else:
                        print 'Malformed PWM command, ignoring:', line

                elif mtc.group('CMD') == 'IRVAL':
                    if mtc.group('QUERY'):
                        qb.send_line('[%s, %s, %s, %s, %s]\n' % qb.get_ir())

                elif mtc.group('CMD') == 'IRDIST':
                    if mtc.group('QUERY'):
                        qb.send_line('[%s, %s, %s, %s, %s]\n' % qb.get_ir_distances())

                elif mtc.group('CMD') == 'ENVAL':
                    if mtc.group('QUERY'):
                        qb.send_line('[%s, %s]\n' % qb.get_ticks())

                elif mtc.group('CMD') == 'ENVEL':
                    if mtc.group('QUERY'):
                        qb.send_line('[%s, %s]\n' % qb.get_speed())

                elif mtc.group('CMD') == 'RESET':
                    qb.reset_ticks()

                elif mtc.group('CMD') == 'END':
                    break

        finally:
            qb.stop()


if __name__ == '__main__':
    import config

    QBServer.run(config)
