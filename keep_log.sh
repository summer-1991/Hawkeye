#!/bin/bash
save_day=7

current_date=$(date -d "${save_day} day ago"  +%Y-%m-%d)
current_time=`date -d "${current_date}" +%s`

folder="/opt/jarvis/logs"
logs=$(ls ${folder})

for log in ${logs}
do 
    log_path="${folder}/${log}"
    log_date=${log#*.}
    log_date=${log_date%.*}
    if [[ ${log_date} =~ "logger" ]];
    then
        continue;
    else
        log_time=`date -d "${log_date}" +%s`
        if [[ ${current_time} -gt ${log_time} ]];
        then
            rm -rf ${log_path};
        else
            continue;
        fi
    fi
done
