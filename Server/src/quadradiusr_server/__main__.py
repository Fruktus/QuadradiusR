import sys

from quadradiusr_server.cli import ServerCli

if __name__ == '__main__':
    exit_code = ServerCli(sys.argv[1:]).run()
    sys.exit(exit_code)
