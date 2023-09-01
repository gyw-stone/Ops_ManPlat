#! /usr/bin/env python
# _*_ coding: utf-8 _*_

import requests
import json
import re
import time
import threading
Auth='a2bb879a3afa51ff6db05e4882f79803f93b4d48af047d026728446bcdc72add'
current_timestamp = int(time.time())
history_timestamp = current_timestamp-(30*24*60*60)

class Zabbix(object):
    def __init__(self, ApiUrl):
        self.ApiUrl = ApiUrl
        self.__Headers = {
            'Content-Type': 'application/json-rpc',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'
        }
        self.__key = [
                                    "system.hostname",    # 主机名
                                    # "system.uptime",      # 系统开机时长
                                    # "io.usedgen[*]",        # 根目录使用率监控
                                    # "disk_capacity.[disk_all_Usage]",#服务器总使用率
                                    "system.cpu.util",    # cpu使用率
                                    "system.cpu.num",     # cpu核数
                                    "system.cpu.load",    # cpu平均负载
                                    # "system.cpu.util[,idle]",     # cpu空闲时间
                                    "vm.memory.utilization",      # 内存使用率
                                    "vm.memory.size[total]",      # 内存总大小
                                    "vm.memory.size[available]",  # 可用内存
                                    # "net.if.in",  # 网卡每秒流入的比特(bit)数
                                    # "net.if.out",  # 网卡每秒流出的比特(bit)数
                                    "gpu.mem.used", # 显存使用率
                                    "gpu.utilisation" # 核心使用率

                                ]
    def GetMonitorHost(self):
        "向host.get接口发起请求，获取所有监控主机"
        HostApiData = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host"],
                "filter": {
                    "ip": ["172.17.45.125","172.26.24.97"],
                    # 'status': 0  # 0 表示启用状态的主机
                },
                "selectInterfaces": ["interfaces", "ip"],
            },
            "auth": Auth,
            "id": 1
        }
        HostRet = requests.post(url=self.ApiUrl, data=json.dumps(HostApiData), headers=self.__Headers).json()
        # print(HostRet)

        if 'result' in HostRet:
            if len(HostRet['result']) != 0:
                # 循环处理每一条记录，进行结构化,最终将所有主机加入到all_host字典中
                Allhost = {}
                for host in HostRet['result']:
                    # host = {'hostid': '10331', 'host': '172.24.125.24', 'name': 'TBDS测试版172.24.125.24', 'interfaces': [{'ip': '172.24.125.24'}]}
                    # 进行结构化，提取需要的信息
                    # HostInfo = {'host': host['host'], 'hostid': host['hostid'], 'ip': host['interfaces'][0]['ip'],
                    #              'name': host['name']}
                    HostInfo = {'host': host['host'], 'hostid': host['hostid'], 'ip': host['interfaces'][0]['ip']}
                    # host_info = {'host': '172.24.125.24', 'hostid': '10331', 'ip': '172.24.125.24', 'name': 'TBDS测试版172.24.125.24'}
                    # 加入到all_host中
                    Allhost[host['hostid']] = HostInfo
                # print(Allhost)
               # {'10823': {'host': '172.17.45.125', 'hostid': '10823', 'ip': '172.17.45.125'},
                # '10837': {'host': '172.26.24.97', 'hostid': '10837', 'ip': '172.26.24.97'}}
                return Allhost
    def GetItem(self):
        " 获取主机的所有监控项 "
        HostRet = self.GetMonitorHost()
        NewAllHost = {}
        # 循环向每个主机发起请求，获取监控项的值
        for k in HostRet:
            ItemData = {
                "jsonrpc": "2.0",
                "method": "item.get",
                "params": {
                    "output": ["extend", "name", "key_", "lastvalue"],
                    "hostids": str(k),
                    "search": {
                        "key_": self.__key
                    },
                    "searchByAny": "true",
                    "sortfield": "name",
                },
                "auth": Auth,
                "id": 1
            }
            # 向每一台主机发起请求，获取监控项
            Ret = requests.post(url=self.ApiUrl, data=json.dumps(ItemData), headers=self.__Headers).json()
            # print(Ret)
            if 'result' in Ret:
                # 判断每台主机是否有获取到监控项，如果不等于0表示获取到有监控项
                if len(Ret['result']) != 0:
                    # 从所有主机信息中取出目前获取信息的这台主机信息存在host_info中
                    HostInfo = HostRet[k]

                    for host in Ret['result']:
                        # 匹配网卡进出流量的正则表达式
                        NetworkBits = re.findall(r'Interface.*: Bits [a-z]{4,8}', str(host.values()))

                        if len(NetworkBits) == 1:
                            HostInfo[host['name']] = host['lastvalue']
                        # elif 'System name' in host.values():      # 匹配主机名，进行保存
                        #     HostInfo[host['name']] = host['lastvalue']
                        # elif 'System uptime' in host.values():  # 匹配系统开机运行时长，进行保存
                        #     HostInfo[host['name']] = host['lastvalue']
                        elif 'Number of CPUs' in host.values():  # 匹配CPU核数，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'Total memory' in host.values():  # 匹配内存总大小，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif '/: Total space' in host.values():  # 匹配根目录总量，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif '/: Used space' in host.values():  # 匹配根目录使用量，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif '/: Space utilization' in host.values():  # 匹配根目录使用量，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        # elif 'Load average (1m avg)' in host.values():  # 匹配CPU平均1分钟负载，进行保存
                        #     HostInfo[host['name']] = host['lastvalue']
                        # elif 'Load average (5m avg)' in host.values():  # 匹配CPU平均5分钟负载，进行保存
                        #     HostInfo[host['name']] = host['lastvalue']
                        elif 'Load average (15m avg)' in host.values():  # 匹配CPU平均15分钟负载，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'CPU idle time' in host.values():  # 匹配CPU空闲时间，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'CPU utilization' in host.values():  # 匹配CPU使用率，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'Memory utilization' in host.values():  # 匹配内存使用率，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'Available memory' in host.values():  # 匹配可用内存大小，进行保存
                            HostInfo[host['name']] = host['lastvalue']
                        elif 'GPU mem usage' in host.values():
                            HostInfo[host['key_']] = host['lastvalue']

                        # elif 'GPU core utilisation' in host.values(): # 匹配核心使用率
                        #     HostInfo[host['name']] = host['lastvalue']
                        elif 'GPU core utilisation' in host.values():  # 匹配核心使用率
                            HostInfo[host['key_']] = host['lastvalue']
            NewAllHost[HostInfo['hostid']] = HostInfo
        # print(NewAllHost)

            return {"Ret":Ret,"Allhost":HostInfo}
    def GetItemValue(self):
        " 输出 {'itemid':value} "
        Ret = self.GetItem()
        NewAllHost1 = {}
        if type(Ret) is dict:
            ids, AllHost = Ret['Ret'], Ret['Allhost']
            for i in range(len(ids['result'])):
                item_id = ids['result'][i]['itemid']
                # print(item_id)
                data1={
                       "jsonrpc": "2.0",
                       "method": "history.get",
                       "params": {
                           "output": "extend",
                           "history": 0,
                           "itemids": item_id,
                           "sortfield": "clock",
                           #"sortorder": "DESC",
                           "time_from": history_timestamp,
                           "time_till": current_timestamp,
                           "limit": 100,
                       },
                       "auth": Auth,
                       "id": 1
                   }
                result1 = requests.post(url=self.ApiUrl, data=json.dumps(data1), headers=self.__Headers).json()
                # print(result1)
                # 处理平均值结果
                average_values = []
                for item in result1['result']:
                    value = float(item['value'])
                    average_values.append(value)
                # print(len(average_values))
                if len(average_values) == 0:
                    average_value = 0
                else:
                    average_value = round(sum(average_values) / len(average_values), 2)
                NewAllHost1[item_id] = average_value
            # print(NewAllHost1)
            return NewAllHost1
    def GetItemValue_30d(self):
        Ret = self.GetItem()
        # print(Ret)
        NewAllHost1 = self.GetItemValue()
        result={}
        last={}
        if type(Ret) is dict:
            ids, AllHost = Ret['Ret'], Ret['Allhost']
            # print(ids)
            # 实现item与name绑定，进行数据处理
            name_mapping = {item['itemid']: item['name'] if not item['name'].startswith('GPU') else item['key_']
                            for item in ids['result']}
            for key, value in NewAllHost1.items():
                if key in name_mapping:
                    result[name_mapping[key]] = value
                else:
                    result[key] = value
            print(result)
            HostInfo1 = AllHost.copy()
            for key, value in result.items():
                if value > 0:
                    if key in HostInfo1:
                        HostInfo1[key] = value
            print(HostInfo1)
        return HostInfo1


if __name__ == "__main__":
    zabbix=Zabbix('http://zabbix.cd.datagrand.com/api_jsonrpc.php')
    zabbix.GetItemValue_30d()
    #zabbix.GetMonitorHost()


""" 问题：两个IP，只有一个IP的值 
    思路：调用history.get哪个函数，最后修正格式
    item产生的值带IP，转换成item：name后直接写入到excel中"""


