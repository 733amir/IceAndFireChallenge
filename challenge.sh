#!/bin/bash

function check_last_command {
    if [ $? -eq 0 ]; then
        echo $1 Started.
    else
        kill $!
        echo $1 Error!
    fi
}

if [ $# -lt 2 ]; then
    echo Usage: './challenge.sh (cpp | java | py | manual) path/to/opponent [path/to/map]'
fi

if [ $# -eq 3 ]; then
    export AICMap=$3
fi

java -jar server/flowsgameserver-v2.0.jar &
server_pid=$!
check_last_command Server
read -p 'Press Enter to run clients...' wait

case $1 in
    cpp)
        $2 &
        ;;
    java)
        java -jar $2 &
        ;;
    py)
        python $2 &
        ;;
    manual)
        $2 &
        ;;
esac

op_pid=$!
check_last_command Opponent
sleep 1
python src/Controller.py &
ai_pid=$!
check_last_command AI

while :; do
    kill -0 $server_pid &> /dev/null
    if [ $? -ne 0 ]; then
        kill $op_pid
        kill $ai_pid
        break
    fi
done
