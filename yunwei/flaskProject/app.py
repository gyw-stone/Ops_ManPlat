import os
import threading
import time
import requests

from flask import Flask, render_template,url_for,session,request
from flaskrr import Get_Host,Get_Rand_ps

class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(*args, **kwargs)
        self._activate_background_job()

    def _activate_background_job(self):
        def run_job():
            while True:
                print('执行后台任务')
                time.sleep(3)

        t1 = threading.Thread(target=run_job)
        t1.start()
#app = Flask(__name__)
app = FlaskApp(__name__)
@app.route('/')
def index():
    return render_template('test.html')
@app.route('/getpasswd',methods=["GET","POST"])
def ViewDiff():
    length = int(request.form["length"])
    password = Get_Rand_ps.generate_random_password(length)
    return render_template("test.html", password=password)
@app.route('/gethost')
def GetHost():
    different_ips_dict = Get_Host.diff_list()
    # 开启自动录入功能
    # Get_Host.Create_host()
    return render_template('diff.html', different_ips_dict=different_ips_dict)
if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)

