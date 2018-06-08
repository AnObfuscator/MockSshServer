# Derived from https://github.com/carletes/mock-ssh-server

import logging
import select
import socket
import threading
import paramiko
import sftp
from mock_ssh_server import datastore

from mock_ssh_server.ssh.constants import SERVER_KEY_PATH

logging.basicConfig()

try:
    from queue import Queue
except ImportError:  # Python 2.7
    from Queue import Queue


__all__ = [
    "SshServer",
]

paramiko.util.log_to_file("server.log")


class ConnectionHandler(paramiko.ServerInterface):
    log = logging.getLogger(__name__)

    def __init__(self, server, client_conn, driver):
        self.server = server
        self.thread = None
        self.command_queues = {}
        client, _ = client_conn
        self.transport = paramiko.Transport(client)
        self.transport.add_server_key(paramiko.RSAKey(filename=SERVER_KEY_PATH))
        self.transport.set_subsystem_handler("sftp", sftp.SFTPServer)
        self._driver = driver

    def run(self):
        self.transport.start_server(server=self)
        while True:
            channel = self.transport.accept()
            if channel is None:
                break
            if channel.chanid not in self.command_queues:
                self.command_queues[channel.chanid] = Queue()
            thread = threading.Thread(target=self.handle_client, args=(channel,))
            thread.setDaemon(True)
            thread.start()

    def handle_client(self, channel):
        try:
            command = self.command_queues[channel.chanid].get(block=True)
            self.log.debug("Executing %s", command)

            stdout, stderr, return_code = self._driver.execute_command(command)

            channel.sendall(stdout)
            channel.sendall_stderr(stderr)
            channel.send_exit_status(return_code)
        except Exception:
            self.log.error("Error handling client (channel: %s)", channel, exc_info=True)
        finally:
            channel.close()

    def check_auth_password(self, username, password):
        try:
            expected_password = datastore.get_password(username)
        except KeyError:
            self.log.debug("Unknown user '%s'", username)
            return paramiko.AUTH_FAILED
        if expected_password == password:
            self.log.debug("Accepting password for user '%s'", username)
            return paramiko.AUTH_SUCCESSFUL
        self.log.debug("Rejecting password for user '%s'", username)
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        try:
            key_path = datastore.get_key_path(username)
            known_public_key = paramiko.RSAKey.from_private_key_file(key_path)
        except KeyError:
            self.log.debug("Unknown user '%s'", username)
            return paramiko.AUTH_FAILED
        if known_public_key == key:
            self.log.debug("Accepting public key for user '%s'", username)
            return paramiko.AUTH_SUCCESSFUL
        self.log.debug("Rejecting public ley for user '%s'", username)
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        self.command_queues.setdefault(channel.get_id(), Queue()).put(command)
        return True

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        return "publickey,password"


class SshServer(object):
    log = logging.getLogger(__name__)

    def __init__(self, host, port, driver):
        self._socket = None
        self._thread = None
        self._host = host
        self._port = port
        self._driver = driver

    def start(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind((self._host, self._port))
        self._socket.listen(5)
        self.log.info('listening on {}...'.format(self._port))
        self._thread = t = threading.Thread(target=self.listen)
        t.setDaemon(True)
        t.start()

    def listen(self):
        while self._socket.fileno() > 0:
            self.log.debug("Waiting for incoming connections ...")
            rlist, _, _ = select.select([self._socket], [], [], 1.0)
            if rlist:
                connection, address = self._socket.accept()
                self.log.debug("... got connection %s from %s", connection, address)
                connection_handler = ConnectionHandler(self, (connection, address), self._driver)
                thread = threading.Thread(target=connection_handler.run)
                thread.setDaemon(True)
                thread.start()

    def stop(self):
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except Exception:
            pass
        self._socket = None
        self._thread = None
