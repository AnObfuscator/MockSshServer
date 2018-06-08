import paramiko


def create_using_private_key(username, private_key_path, host, port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host,
                   port=port,
                   username=username,
                   key_filename=private_key_path,
                   allow_agent=False,
                   look_for_keys=False)
    return client


def create_using_password(username, password, host, port):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host,
                   port=port,
                   username=username,
                   password=password,
                   allow_agent=False,
                   look_for_keys=False)
    return client
