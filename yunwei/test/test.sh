#!/bin/bash

harbor_url="https://dockerhub.datagrand.com"
harbor_username="admin"
harbor_password="AYLyR89wmmMlVFwa"
delete_file="2_delete.txt"
max_procsses=20

while IFS= read -r image; do

    curl -u "$harbor_username:$harbor_password" -X DELETE "$harbor_url/api/repositories/$image" && echo "镜像已删除：$image" >> already_delete.txt &
    ps -p $! > /dev/null
    if [ $processes -ge $max_processes ]; then
  			wait
  	processes=$((processes-1))
  	fi
  	processes=$((processes+1))

done < "$delete_file"

