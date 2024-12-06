import os
import threading
import time,logging
import requests,jsonify
import pandas as pd

from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, url_for, session, request, jsonify, make_response, flash, redirect

from flaskrr import Get_Host, Get_Rand_ps,Create_Zabbix_Host_1,Mod_domain,Add_git_user

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self._activate_background_job()

    def _activate_background_job(self):
        def run_job():
            while True:
                print('执行后台任务')
                time.sleep(20)

        t1 = threading.Thread(target=run_job)
        t1.start()

app = FlaskApp(__name__)
# 配置日志
log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, 'flask_app.log')
handler = logging.FileHandler(log_file)
handler.setLevel(logging.DEBUG)  # 设置日志级别，可以设置为 DEBUG, INFO, WARNING 等
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# 将 handler 添加到 Flask 的默认 logger
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

# 自定义key
app.secret_key = 'FpC4sK0IBVgbeXw8j8iehoEp4awsdPsv'
# 模拟用户名和密码
USERNAME = 'admin@datagrand.com'
PASSWORD = 'qwer1234'

# set expired time 6 hours
EXPIRATION_TIME = timedelta(hours=6)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or 'expires_at' not in session:
            return redirect(url_for('login'))
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.utcnow() > expires_at:
            session.clear()
            flash('Your session has expired. Please log in again.')
            return redirect(url_for('login'))
        
        # 更新最后活动时间
        session['expires_at'] = (datetime.utcnow() + EXPIRATION_TIME).isoformat()
        return f(*args, **kwargs)

    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            session['expires_at'] = (datetime.utcnow() + EXPIRATION_TIME).isoformat()
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials, please try again.')
    return render_template('login.html')
@app.route('/')
@login_required
def index():
    return render_template('test.html')

@app.route('/getpasswd', methods=["GET", "POST"])
@login_required
def ViewDiff():
    length = int(request.form["length"])
    pwd_types = request.form["pwd_type"] 
    password = Get_Rand_ps.generate_random_password(length,pwd_types)
    return render_template("test.html", password=password)


@app.route('/gethost',methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def Create_domaindiy_text():
    result = None
    error_message = None

    if request.method == 'POST':
        file_name = request.form["filename"]
        nginx_config = request.form["nginx_config"]
        tocol = request.form["tocol"]
        #print("nginx_config:", nginx_config)
        nginx_config = nginx_config.replace('\r', '')
        try:
            response = Mod_domain.ssh_connect_and_execute_commands_text(file_name, nginx_config, tocol)
            if response: 
                data = response.get_json()
                error_message = data.get('error','')
        except Exception as e:
            error_message = f"SSH connection or command execution error: {e}"
    return render_template('mod_domain_text.html', error_message=error_message)
# 读取数据文件
@app.route('/gethost/data')
@login_required
def get_data():
    # 读取 CSV 文件
    file_path = '/opt/shell/host1s_info.csv'
    
    try:
        data = pd.read_csv(file_path)
        #print(data)  # 打印数据以检查读取是否成功
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        data = pd.DataFrame()  # 如果读取失败，初始化一个空的 DataFrame
    
    # 将数据转化为 HTML 表格
    html_table = data.to_html(classes='data', header=True, index=False)
    html_table = html_table.replace('\n', '').replace("['", '').replace(']', '') 
    return render_template('data_table.html', tables=[html_table])

# git add new user
@app.route('/create/adduser', methods=['GET', 'POST'])
@login_required
def add_user():
    error_message = None
    if request.method == 'POST':
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]

        try:
            git = Add_git_user.GitLabUser()  # 实例化类
            response = git.addUser(name, username, email)  # 调用方法
            if response:
                data = response.get_json()
                error_message = data.get('error', '')
        except Exception as e:
            error_message = f"Check your token is expired? {str(e)}"
    
    # 确保这里的缩进正确
    return render_template('add_user.html', error_message=error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True,threaded=True)
