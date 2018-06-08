import os
from multiprocessing import RLock

KEY_DIR = os.path.join(os.path.dirname(__file__), "keys")
if not os.path.exists(KEY_DIR):
    os.makedirs(KEY_DIR)

_known_commands = {}
_cmd_lock = RLock()

_known_users = {}
_usr_lock = RLock()

_key_lock = RLock()


def add_command(command):
    _cmd_lock.acquire()
    try:
        global _known_commands
        _known_commands[command['input']] = command
    finally:
        _cmd_lock.release()


def get_command(value):
    _cmd_lock.acquire()
    try:
        global _known_commands
        return _known_commands.get(value, None)
    finally:
        _cmd_lock.release()


def get_commands():
    _cmd_lock.acquire()
    try:
        global _known_commands
        return _known_commands.values()
    finally:
        _cmd_lock.release()


def clear_commands():
    _cmd_lock.acquire()
    try:
        global _known_commands
        _known_commands.clear()
    finally:
        _cmd_lock.release()


def add_user(user):
    _usr_lock.acquire()
    try:
        global _known_users
        _known_users[user['username']] = user['password']
    finally:
        _usr_lock.release()


def get_user(user):
    _usr_lock.acquire()
    try:
        global _known_users
        return _known_users[user]
    finally:
        _usr_lock.release()


def get_users():
    _usr_lock.acquire()
    try:
        global _known_users
        return _known_users.values()
    finally:
        _usr_lock.release()


def clear_users():
    _usr_lock.acquire()
    try:
        global _known_users
        _known_users.clear()
    finally:
        _usr_lock.release()


def add_key(key):
    _key_lock.acquire()
    try:
        filename = '{}.pub'.format(key['user'])
        full_path = os.path.join(KEY_DIR, filename)
        with open(full_path, "w+") as key_file:
            key_file.writelines(key['key'])
    finally:
        _key_lock.release()


def get_key_path(user):
    _key_lock.acquire()
    try:
        filename = '{}.pub'.format(user)
        return os.path.join(KEY_DIR, filename)
    finally:
        _key_lock.release()


def get_password(user):
    _usr_lock.acquire()
    try:
        return _known_users[user]
    finally:
        _usr_lock.release()


def get_keys():
    _key_lock.acquire()
    try:
        return os.listdir(KEY_DIR)
    finally:
        _key_lock.release()


def clear_keys():
    _key_lock.acquire()
    try:
        for the_file in os.listdir(KEY_DIR):
            file_path = os.path.join(KEY_DIR, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
    finally:
        _key_lock.release()
