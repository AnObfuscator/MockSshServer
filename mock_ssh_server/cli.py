import os

import argh as argh
from ssh.server import SshServer
from ssh.drivers import PlaybackDriver, RecordDriver, LocalDriver
import ssh.client
from api import app


@argh.arg('--host', default='localhost', help='')
@argh.arg('--http-port', default=5000, help='')
@argh.arg('--ssh-port', default=59484, help='')
def playback(host=None, http_port=None, ssh_port=None):
    driver = PlaybackDriver()
    server = SshServer(host, ssh_port, driver)
    server.start()
    api_server = app.create()
    api_server.run(host=host, port=http_port, debug=False)
    server.stop()
    print('Stopped')


@argh.arg('--host', default='localhost', help='')
@argh.arg('--http-port', default=5000, help='')
@argh.arg('--ssh-port', default=59484, help='')
@argh.arg('--record-dir', default='', help='')
@argh.arg('--auth-type', choices=['key', 'pass'], default='pass')
@argh.arg('--remote-host', default='localhost', help='')
@argh.arg('--remote-port', default=22, help='')
def record(host=None, http_port=None, ssh_port=None, record_dir=None, auth_type='pass', remote_host=None, remote_port=22):
    if auth_type == 'pass':
        username = os.environ.get('REMOTE_USER')
        password = os.environ.get('REMOTE_PASS')
        ssh_client = ssh.client.create_using_password(username, password, remote_host, remote_port)
    elif auth_type == 'key':
        username = os.environ.get('REMOTE_USER')
        key_path = os.environ.get('REMOTE_KEY_PATH')
        ssh_client = ssh.client.create_using_private_key(username, key_path, remote_host, remote_port)
    else:
        raise NotImplementedError

    if not record_dir:
        record_dir = os.path.join(os.path.dirname(__file__), "recordings")
    if not os.path.exists(record_dir):
        os.makedirs(record_dir)

    driver = RecordDriver(ssh_client, record_dir)
    server = SshServer(host, ssh_port, driver)
    server.start()
    api_server = app.create()
    api_server.run(host=host, port=http_port, debug=False)
    server.stop()
    print('Stopped')


@argh.arg('--host', default='localhost', help='')
@argh.arg('--http-port', default=5000, help='')
@argh.arg('--ssh-port', default=59484, help='')
def local(host=None, http_port=None, ssh_port=None):
    driver = LocalDriver()
    server = SshServer(host, ssh_port, driver)
    server.start()
    api_server = app.create()
    api_server.run(host=host, port=http_port, debug=False)
    server.stop()
    print('Stopped')


def main():
    parser = argh.ArghParser()
    parser.add_commands([playback, record, local])
    parser.dispatch()


if __name__ == '__main__':
    main()
