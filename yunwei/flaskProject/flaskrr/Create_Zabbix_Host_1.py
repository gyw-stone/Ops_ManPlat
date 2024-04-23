import json
import requests


def Create_host(ip,value,os_type):
    # 设置 Zabbix API 访问参数
    api_url = 'http://zabbix.cd.datagrand.com/api_jsonrpc.php'
    auth_token = '8179fd5daa4ad44f631acb13f163e9e3e4d69f66dc0cb9f62231320fe6e51ca5'

    # 构建 API 请求体
    headers = {'Content-Type': 'application/json-rpc'}

    # 构建 templates 字段的内容，根据是否传入 template 进行判断
    # 根据操作系统类型选择相应的模板ID
    if os_type == "windows":
        template_id = "10081"  # Windows 模板
    else: 
        template_id = "10001"
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

