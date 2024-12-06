import ssl
import requests
import re
import os

from pyVmomi import vim
from pyVim import connect
import threading
from datetime import datetime
import concurrent.futures
"""
实现获取vcenter开机机器的文件名，责任人以及结束日期
判断结束日期是否小于7天来触发提醒规则--发送到钉钉群
"""

# 使用环境变量来存储敏感信息
host = os.getenv('VCENTER_HOST', '172.26.23.210')
user = os.getenv('VCENTER_USER', 'guoyaowen@vsphere.local')
password = os.getenv('VCENTER_PASSWORD', 'DataGrand@123')
webhook_url = os.getenv('DINGTALK_WEBHOOK_URL', 'https://oapi.dingtalk.com/robot/send?access_token=e58087b31e6c331e28b8d5f802c5dc6426bb20b24a829101f7a243745366246c')

class VCenterHostGetter:
    """ 获取主机名以及对应的IP地址 """
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def process_vm(self, vm):
        vm_info = []
        if vm.runtime.powerState == "poweredOn":
            vm_name = vm.name
            beizhu = vm.summary.config.annotation
            resp_person,end_date_str=self.process_data(beizhu)
            match = re.search(r'(\d+)(?:_(\d+))?', vm_name)
            if match:
                first_number = match.group(1)
                second_number = match.group(2)
                if second_number:
                    if first_number.startswith('200'):
                        ip_address = f"172.16.{first_number}.{second_number}"
                    else:
                        ip_address = f"172.26.{first_number}.{second_number}"
                else:
                    ip_address = f"172.16.200.{first_number}"
            else:
                ip_address = ""

            vm_info.append([vm_name,ip_address, resp_person,end_date_str])
        # print(vm_info)
        return vm_info


    def process_data(self,annotation):
        resp_person = None
        end_date_str = None
        # 只要责任人和结束日期两行
        for line in annotation.split('\n'):
            if line.startswith('责任人：'):
                resp_person = line.split('：')[1].strip()
            elif line.startswith('结束日期：') or line.startswith('结束时间：'):
                end_date_str = line.split('：')[1].strip()
        return resp_person, end_date_str
    def get_host_info(self):
        # 定义 SSL 协议
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        try:
            # 连接到 vCenter
            si = connect.SmartConnect(host=self.host,user=self.user,
                                      pwd=self.password,port=443,
                                      sslContext=context)

            # 获取 vCenter 中的虚拟主机（虚拟机）
            content = si.RetrieveContent()
            vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
            vms = vm_view.view
            with concurrent.futures.ThreadPoolExecutor() as executor:
                vm_info_list = list(executor.map(self.process_vm, vms))
            vm_info_list = [item for sublist in vm_info_list for item in sublist]
        finally:
            connect.Disconnect(si)

        # print(vm_info_list)
        return vm_info_list

def parse_date(date_str):
    date_formats = [
        '%Y年%m月%d日',
        '%Y年%m月%d',
        '%Y-%m-%d',
        '%Y%m%d'
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None
def fix_date(data):
    processed_data = []
    current_date = datetime.now()
    for item in data:
        end_date_str = item[3]
        # 将"xx年xx月xx日"替换为具体日期
        if end_date_str is not None:
            if "20" in end_date_str:
                end_date_str = end_date_str.replace("20", f"{current_date.year // 100}")
            end_date = parse_date(end_date_str)
            if end_date is None:
                continue
            if (end_date - current_date).days < 7:
                processed_data.append([item[0], item[1], item[2],end_date_str])

    # print(processed_data)
    return processed_data


def send_to_dingtalk(data):
    headers = {'Content-Type': 'application/json'}

    messages = []
    for item in data:
        message = f"主机名: {item[0]}\nIP: {item[1]}\n责任人: {item[2]}\n结束日期: {item[3]}"
        messages.append(message)

    payload = {
        "msgtype": "text",
        "text": {
            "content": "\n\n".join(messages)
        },
        "at": {
            "isAtAll": True
        }
    }

    response = requests.post(webhook_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("消息发送成功！")
    else:
        print(f"消息发送失败，错误码: {response.status_code}")


if __name__=='__main__':
    # 使用示例
    host_getter = VCenterHostGetter(host, user, password)
    a=host_getter.get_host_info()
    data = fix_date(a)
    send_to_dingtalk(data)






