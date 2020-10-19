#!/bin/bash
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

if [ "$1" -eq 1 ];then
    export FLASK_APP=manage.py
    flask initdata
fi
deactivate