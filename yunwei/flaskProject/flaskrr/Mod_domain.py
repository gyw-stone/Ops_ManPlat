import paramiko
import re

def ssh_connect_and_execute_commands(ip, new_server_name, new_domain, port, tocol):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host="172.26.24.72"
    username = "root"
    password = "EQ9yqheD4qFWkd6dZC14"
    try:
        ssh.connect(host, username=username, password=password,timeout=10)
        # 检查自定义名字.conf文件是否存在
        custom_conf_name = f"{new_server_name}.conf"
        check_existence_command = f"ls /root/test_git/{custom_conf_name} > /dev/null 2>&1 && echo exists || echo not_exists"
        stdin, stdout, stderr = ssh.exec_command(check_existence_command)
        output = stdout.read().decode().strip()
        custom_domin = f"{new_domain}.datagrand.com"

        if output == "exists":
            print(f"File {custom_conf_name} already exists. Skipping template copy and modification.")
        else:

            if tocol == "https":
                tempfile = "/root/test_git/https.template"
            else:
                 tempfile = "/root/test_git/http.template"

            # 执行命令：复制模板文件并重命名
            ssh.exec_command(f"cp {tempfile} /root/test_git/{custom_conf_name}")

            # 执行命令：使用sed替换server_name
            sed_command = f"sed -i 's/server_name domain;/server_name {custom_domin};/' /root/test_git/{custom_conf_name}"
            ssh.exec_command(sed_command)

            # 执行命令：使用sed替换proxy_pass
            sed_command = f"sed -i 's|proxy_pass http://ip:port/;|proxy_pass http://{ip}:{port}/;|' /root/test_git/{custom_conf_name}"
            ssh.exec_command(sed_command)
            # # 执行命令：检查Nginx配置
            # stdin, stdout, stderr = ssh.exec_command("nginx -t")
            #
            # # 检查输出以确定是否有错误
            # output = stdout.read().decode().strip()
            # error = stderr.read().decode().strip()
            #
            # if re.search(r"test is successful", output, re.IGNORECASE):
            #     print("Nginx configuration test passed.")
            #     # 执行命令：重新加载Nginx配置
            #     ssh.exec_command("nginx -s reload")
            #     print("Nginx configuration reloaded.")
            # else:
            #     print("Nginx configuration test failed:")
            #     print(output)
            #     print(error)
            #     raise Exception("Nginx configuration check failed.")

    except Exception as e:
        print(f"SSH connection or command execution error: {e}")
    finally:
        ssh.close()
