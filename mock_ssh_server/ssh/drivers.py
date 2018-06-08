import json
import os
import subprocess

import mock_ssh_server.datastore as datastore


class Driver:
    def execute_command(self, command):
        raise NotImplementedError


class LocalDriver(Driver):
    def execute_command(self, command):
        p = subprocess.Popen(command, shell=True,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return_code = p.returncode
        return stdout, stderr, return_code


class RecordDriver(Driver):
    def __init__(self, ssh_client, record_dir):
        self.client = ssh_client
        self.record_dir = record_dir

    def execute_command(self, command):
        stdin_c, stdout_c, stderr_c = self.client.exec_command(command)

        stdin = command
        stdout = stdout_c.read()
        stderr = stderr_c.read()

        self._save_command_to_file(stdin, stdout, stderr)

        return stdout, stderr, 0

    def _save_command_to_file(self, stdin, stdout, stderr):

        command_obj = {
          "input": stdin,
          "stdout": stdout,
          "stderr": stderr,
          "exitCode": 0  # TODO
        }
        command_json = json.dumps(command_obj)

        file_path = self._file_path_for_new_recording(stdin)
        with open(file_path, "w+") as out_file:
            out_file.writelines(command_json)

    def _file_path_for_new_recording(self, stdin):
        count = 0
        file_name = stdin.replace(' ', '_') + str(count) + '.json'
        while os.path.exists(os.path.join(self.record_dir, file_name)):
            count += 1
            file_name = stdin.replace(' ', '_') + str(count) + '.json'

        return os.path.join(self.record_dir, file_name)


class PlaybackDriver(Driver):
    def execute_command(self, command):
        command_result = datastore.get_command(command)
        print('got command: {}'.format(command))
        print('Availabile commands: {}'.format(len(datastore._known_commands)))
        if command_result is None:
            print('command not found')
            raise Exception('Command not found: {}'.format(command))
        print(command_result)
        return command_result['stdout'], command_result['stderr'], command_result['exitCode']
