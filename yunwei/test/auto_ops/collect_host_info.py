#!/usr/bin/python3
# -*- coding: utf-8 -*-
import psutil
# 1.内存使用率
# 2.磁盘使用率
# 3.系统负载，过去5分钟
def get_data():
  mem = psutil.virtual_memory()
  mem_percent = mem.percent
  
