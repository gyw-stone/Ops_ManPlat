import os
import threading
import time
import requests

from flask import Flask, render_template, url_for, session, request, jsonify, make_response
from flaskrr import Get_Host, Get_Rand_ps,Create_Zabbix_Host_1,Mod_domain

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self._activate_background_job()

    def _activate_background_job(self):
        def run_job():
            while True:
                print('执行后台任务')
                time.sleep(10)

        t1 = threading.Thread(target=run_job)
        t1.start()


# app = Flask(__name__)
app = FlaskApp(__name__)


@app.route('/')
def index():
    return render_template('test.html')


@app.route('/getpasswd', methods=["GET", "POST"])
def ViewDiff():
    length = int(request.form["length"])
    pwd_types = request.form["pwd_type"] 
    password = Get_Rand_ps.generate_random_password(length,pwd_types)
    return render_template("test.html", password=password)


@app.route('/gethost',methods=["GET", "POST"])
def GetHost():
   # different_ips_dict = Get_Host.diff_list()
    result=None
    if request.method == 'POST':
       answer = request.form["answer"]
       print("answer is :",answer)
       if answer=='YES':
          result = Get_Host.Create_host()
          print("Result from Create_host:",result)
          
    different_ips_dict = Get_Host.diff_list()
    return render_template('diff.html', result=result,different_ips_dict=different_ips_dict)


@app.route('/gethost/createhost', methods=["GET", "POST"])
def Auto_Create1():
    result = None
    if request.method == 'POST':
        IP = request.form["IP"]
        name = request.form["name"]
        os_type = request.form["os_type"]
        print("IP:",IP, "name:",name,"os_type:",os_type)
        result = Create_Zabbix_Host_1.Create_host(IP, name,os_type)
    return render_template('createhost.html', result=result)
# 实现网页写入域名到服务器中
@app.route('/create/domaindiy', methods=["GET", "POST"])
def Create_domaindiy():
    result=None
    if request.method == 'POST':
       IP = request.form["IP"]
       file_name = request.form["filename"]
       new_domain = request.form["domainname"]
       port = request.form["port"]
       tocol = request.form["tocol"]
       result = Mod_domain.ssh_connect_and_execute_commands(IP,file_name,new_domain,port, tocol)
    return render_template('mod_domain.html',result=result)
# 实现网页写入域名到服务器中-文本形式
@app.route('/create/domaindiy/file', methods=["GET", "POST"])
def Create_domaindiy_text():
    result = None
    error_message = None

    if request.method == 'POST':
        file_name = request.form["filename"]
        nginx_config = request.form["nginx_config"]
        tocol = request.form["tocol"]
        print("nginx_config:", nginx_config)
        try:
            response = Mod_domain.ssh_connect_and_execute_commands_text(file_name, nginx_config, tocol)
            if response: 
                data = response.get_json()
                error_message = data.get('error','')
        except Exception as e:
            error_message = f"SSH connection or command execution error: {e}"
    return render_template('mod_domain_text.html', error_message=error_message)
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
