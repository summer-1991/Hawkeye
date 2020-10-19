#!/bin/bash
APP_NAME=jarvis
PROJECT_LOCATION=/opt/jarvis/Manage

usage()
{
   echo "Usage: sh ִÐ½ű¾.sh[start|stop|restart|status]"
   exit 1
}

is_exist()
{
   pid=`ps -ef | grep $APP_NAME | grep -v grep | awk '{print $2}'`
   if [ -z "${pid}" ]; then
     proct=1
   else
     proct=0
   fi
}

start()
{
   is_exist
   if [ $proct -eq 0 ]; then
     echo "${APP_NAME} is already running. pid=${pid} ."
   else
     cd ${PROJECT_LOCATION}
     source venv/bin/activate
     # export FLASK_APP=manage.py
     # flask initdata
     nohup gunicorn -c gunicorn_config.py manage:app >nohup.out 2>&1 &
   fi
}

stop()
{
   is_exist
   if [ $proct -eq 0 ]; then
      cd ${PROJECT_LOCATION}
      kill -9 $pid
      echo "${APP_NAME} is stop"
   else
      echo "${APP_NAME} is not running"
   fi
}

status()
{
   is_exist
   if [ $proct -eq 0 ]; then
      echo "${APP_NAME} is running. Pid is ${pid}"
   else
      echo "${APP_NAME} is NOT running."
   fi
}

restart()
{
   stop
   start
}

case "$1" in
   "start")
      start
      ;;
   "stop")
      stop
      ;;
   "status")
      status
      ;;
   "restart")
      restart
      ;;
   * )
      usage
      ;;
esac
