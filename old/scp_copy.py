import os
import paramiko
server = 'ermopi.local'
username = 'ermopi'
password = 'findelmundo2526'
remotePath = '/home/ermopi/ermoapp/'
localPath = '/home/veuc7913/Documents/python/ermoapp/'


def copy_to(filename):
    local_path = localPath + filename
    remote_path = remotePath + filename

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(
        os.path.join("~", ".ssh", "known_hosts")))

    ssh.connect(server, username=username, password=password)
    sftp = ssh.open_sftp()

    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()


def copy_from(filename):
    local_path = localPath + filename
    remote_path = remotePath + filename

    ssh = paramiko.SSHClient()
    ssh.load_host_keys(os.path.expanduser(
        os.path.join("~", ".ssh", "known_hosts")))

    ssh.connect(server, username=username, password=password)
    sftp = ssh.open_sftp()

    sftp.get(remote_path, local_path)
    sftp.close()
    ssh.close()


copy_to('ermoapp.py')

copy_from('ermoapp.py')
