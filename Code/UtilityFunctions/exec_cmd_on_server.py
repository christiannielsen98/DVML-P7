from UtilityFunctions.run_query import run_query
import paramiko


def exec_cmd_on_server(cmd_to_execute: str):
    host = '10.92.0.48'
    user = 'ubuntu'
    keyfilename = '/Users/christiannielsen/Library/CloudStorage/OneDrive-AalborgUniversitet/DVML-P7/P7.pem'
    # cmd_to_execute = f'docker exec -i vos isql 1111 exec="{sparql_query}"'
    cmd_to_execute = f"""{cmd_to_execute}"""

    ssh = paramiko.SSHClient()
    k = paramiko.RSAKey.from_private_key_file(keyfilename)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, pkey=k)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    print(f'STDOUT: \n{ssh_stdout.read().decode("utf8")}')
    print(f'STDERR: \n{ssh_stderr.read().decode("utf8")}')
    # Get return code from command (0 is default for success)
    print(f'Return code: \n{ssh_stdin.channel.recv_exit_status()}')
    return ssh_stdout

def exec_sparql_on_server(sparql_query: str):
    host = '10.92.0.48'
    user = 'ubuntu'
    keyfilename = '/Users/christiannielsen/Library/CloudStorage/OneDrive-AalborgUniversitet/DVML-P7/P7.pem'
    # cmd_to_execute = f'docker exec -i vos isql 1111 exec="{sparql_query}"'
    cmd_to_execute = f"""cd /home/ubuntu/DVML-P7/Code; python3.10 -c 'from UtilityFunctions.run_query import run_query; run_query(query="{sparql_query}", as_dataframe=False, do_print=True)'"""

    ssh = paramiko.SSHClient()
    k = paramiko.RSAKey.from_private_key_file(keyfilename)

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, pkey=k)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    print(f'STDOUT: \n{ssh_stdout.read().decode("utf8")}')
    print(f'STDERR: \n{ssh_stderr.read().decode("utf8")}')
    # Get return code from command (0 is default for success)
    print(f'Return code: \n{ssh_stdin.channel.recv_exit_status()}')
    return ssh_stdout