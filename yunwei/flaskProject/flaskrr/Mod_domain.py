import paramiko
import re
from flask import jsonify, make_response
def establish_ssh_connection():
    """建立SSH连接"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = "172.16.200.126"
    username = "root"
    private_key_path = "/root/.ssh/id_rsa"

    with open(private_key_path, "r") as key_file:
        private_key = paramiko.RSAKey.from_private_key(key_file)
    ssh.connect(hostname=host, username=username, pkey=private_key, timeout=10)
    return ssh
def check_and_handle_config_file(ssh, filename, error_message, response_code):
    """检查配置文件是否存在并处理"""
    check_command = f"ls /etc/nginx/conf.d/{filename} > /dev/null 2>&1 && echo exists || echo not_exists"
    stdin, stdout, stderr = ssh.exec_command(check_command)
    output = stdout.read().decode().strip()

    if output == "exists":
        return make_response(jsonify({'error': error_message}), response_code)

    return None
def execute_commands_and_check_nginx(ssh, commands, final_message="Nginx configuration reloaded."):
    """执行一系列命令并检查Nginx配置"""
    try:
        for cmd in commands:
            ssh.exec_command(cmd)

        # 检查Nginx配置
        nginx_test_command = "nginx -t"
        stdin, stdout, stderr = ssh.exec_command(nginx_test_command)
        output = stdout.read().decode('gbk').strip()
        error = stderr.read().decode('gbk').strip()
        if "syntax is ok" in error and "test is successful" in error:
            print("Nginx configuration test passed.")
            ssh.exec_command("nginx -s reload")
            print(final_message)
        else:
            print("Nginx configuration test failed:")
            print(output)
            print(error)
            raise Exception("Nginx configuration check failed.")
    finally:
        ssh.close()
def ssh_connect_and_execute_commands(ip, new_server_name, new_domain, port, tocol):
    ssh = establish_ssh_connection()
    if ssh is None:
        return  # 或者处理无法建立连接的情况

    custom_conf_name = f"{new_server_name}.conf"
    if check_and_handle_config_file(ssh, custom_conf_name, f'File {custom_conf_name} already exists.', 404):
        return

    commands = []
    if tocol == "https":
        commands.append(f"cp /etc/nginx/conf.d/template/https.template /etc/nginx/conf.d/{custom_conf_name}")
        last_segment = new_domain.split('.')[-1]
        if last_segment == 'cn':
            commands.append(
                f"sed -i 's|datagrand.com.pem;|ssl_cn/datagrand.cn.pem;|; s|datagrand.com.key;|ssl_cn/datagrand.cn.key;|' /etc/nginx/conf.d/{custom_conf_name}")
    else:
        commands.append(f"cp /etc/nginx/conf.d/template/http.template /etc/nginx/conf.d/{custom_conf_name}")

    commands.extend([
        f"sed -i 's/server_name domain;/server_name {new_domain};/' /etc/nginx/conf.d/{custom_conf_name}",
        f"sed -i 's|proxy_pass http://ip:port/;|proxy_pass http://{ip}:{port}/;|' /etc/nginx/conf.d/{custom_conf_name}"
    ])

    execute_commands_and_check_nginx(ssh, commands)
def ssh_connect_and_execute_commands_text(new_filename, text, tocol):
    ssh = establish_ssh_connection()
    if ssh is None:
        return

    custom_conf_name = f"{new_filename}.conf"
    if check_and_handle_config_file(ssh, custom_conf_name, f'File {custom_conf_name} already exists.', 404):
        return

    directory = "/etc/nginx/stream.d/" if tocol == "TCP" else "/etc/nginx/conf.d/"
    command = f"echo '{text}' >> {directory}{custom_conf_name}"
    execute_commands_and_check_nginx(ssh, [command])

