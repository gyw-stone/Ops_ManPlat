#!/bin/bash

# 获取当前目录下的所有文件和文件夹进行同步
for subfile in `ls`
do
    # 启动 rsync 并将进程放到后台执行
    rsync -avr "${subfile}" user@a.b.c.d:/data/mongo/105xml/ &

    # 检查当前运行的 rsync 进程数
    sync_proc_num=$(ps --no-header -C rsync -o pid | wc -l)
    
    # 如果运行的 rsync 进程数超过或等于8，则等待
    while [ "$sync_proc_num" -ge 8 ]
    do
       sleep 60  # 等待60秒后再检查
       sync_proc_num=$(ps --no-header -C rsync -o pid | wc -l)
    done
done

# 等待所有后台进程结束
wait

