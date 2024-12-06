import requests
import json
import ssl
import re
import threading
import concurrent.futures

from pyVmomi import vim
from pyVim import connect
from .check_os_type import check_os_type
from .host_notify import VCenterHostGetter
def zabbix_gethost():
    """ 获取zabbix chengdu_server主机组的所有启用状态的主机"""
    # 设置 Zabbix API 访问参数
    #api_url = 'http://zabbix.cd.datagrand.com/api_jsonrpc.php'
    api_url = 'http://172.16.200.199:8080/api_jsonrpc.php'
    auth_token = '8179fd5daa4ad44f631acb13f163e9e3e4d69f66dc0cb9f62231320fe6e51ca5'

    # 构建 API 请求体
    headers = {'Content-Type': 'application/json-rpc'}
    data = {
        'jsonrpc': '2.0',
        'method': 'host.get',
        'params': {
            'output': ['hostid', 'host', 'name'],
            'groupids': "19",
        },
        'auth': auth_token,
        'id': 1
    }

    # 发送 API 请求
    response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False, timeout=10)
    result = response.json()

    # 存储列表
    s3 = []

    # 处理 API 响应
    if 'result' in result:
        hosts = result['result']
        for host in hosts:
            if host['hostid'] == '10463':
                pass
            else:
                s3.append([host['host'], host['name']])
    else:
        print(f"API Request Error: {result['error']['message']}")
    # print(s3)
    return s3
# class VCenterHostGetter:
#     """ 获取主机名以及对应的IP地址 """
#     def __init__(self, host, user, password):
#         self.host = host
#         self.user = user
#         self.password = password
#
#     def process_vm(self, vm):
#         vm_info = []
#         if vm.runtime.powerState == "poweredOn":
#             vm_name = vm.name
#
#             for network in vm.guest.net:
#                 ip_address = str(network.ipAddress)
#                 ip_matches = re.findall(r'\d+\.\d+\.\d+\.\d+', ip_address)
#                 if ip_matches:
#                     ip_address = ip_matches[0]
#                 elif not ip_address:
#                     # 从 vm_name 中提取两个数字部分
#                     match = re.search(r'(\d+)_(\d+)', vm_name)
#                     if match:
#                         first_number, second_number= match.group
#                         ip_address = f"172.26.{first_number}.{second_number}"
#
#                 if ip_address and not ip_address.endswith(".1") and  ip_address.startswith("172"):
#                         vm_info.append([vm_name, ip_address])
#
#         # print(vm_info)
#         return vm_info
#
#     def get_host_info(self):
#             # 定义 SSL 协议
#             context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
#             context.verify_mode = ssl.CERT_NONE
#
#             # 连接到 vCenter
#             try:
#                 si = connect.SmartConnect(host=self.host, user=self.user, pwd=self.password, port=443,
#                                           sslContext=context)
#                 content = si.RetrieveContent()
#                 vm_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
#                 vms = vm_view.view
#
#                 with concurrent.futures.ThreadPoolExecutor() as executor:
#                     vm_info_list = list(executor.map(self.process_vm, vms))
#
#                 vm_info_list = [item for sublist in vm_info_list for item in sublist]
#             finally:
#                 connect.Disconnect(si)
#
#             # print(vm_info_list)
#
#             return vm_info_list

def diff_list():
    """ 实现获取两个列表不同的值并输出到一个文档中 """
    host = '172.26.23.210'
    user = 'guoyaowen@vsphere.local'
    password = 'DataGrand@123'

    host_getter = VCenterHostGetter(host, user, password)
    list1 = zabbix_gethost()
    vm_info_list = host_getter.get_host_info()
    vm_info_list = [row[:2] for row in vm_info_list]
    # 提取第一个列表中的 IP 地址
    ip_list1 = [item[0] for item in list1]
    # 创建空字典
    different_ips_dict = {}
    def process(item):
        ip = item[1]
        key = item[0]
        if len(item) > 1 and item[1] not in ip_list1:
            if ip.startswith("172.16.83"):
                return
            elif ip is None:
                return
            else:
                different_ips_dict[ip] = key

    threads = []
    for item in vm_info_list:
        t = threading.Thread(target=process, args=(item,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    return different_ips_dict


def Create_host():
    """ 实现批量录入主机信息到zabbix,存在问题，重复录入，并且录入的IP为名字 """

    dict1 = diff_list()
    # 设置 Zabbix API 访问参数
    api_url = 'http://zabbix.cd.datagrand.com/api_jsonrpc.php'
    auth_token = '8179fd5daa4ad44f631acb13f163e9e3e4d69f66dc0cb9f62231320fe6e51ca5'

    # 构建 API 请求体
    headers = {'Content-Type': 'application/json-rpc'}
    for ip, value in dict1.items():
        if ip is None:
            continue
        else:
            template_id = check_os_type(ip)
            data = {
                "jsonrpc": "2.0",
                "method": "host.create",
                "params": {
                    "host": ip,
                    "name": value,
                    "interfaces": [
                        {
                            "type": 1,
                            "main": 1,
                            "useip": 1,
                            "ip": ip,
                            "dns": "",
                            "port": "10050"
                        }
                    ],
                    "groups": [
                        {
                            "groupid": "19"
                        }
                    ],
                    "templates": [
                        {
                            "templateid": template_id
                        }
                    ],
                },
                "auth": auth_token,
                "id": 1
            }
        response = requests.post(api_url, headers=headers, data=json.dumps(data), verify=False)
        if response.status_code != 200:
           raise Exception("Request failed!")
        result = response.json()
	
        #print(result)
