#!/bin/bash

function check_last_command {
    if [ $? -eq 0 ]; then
        echo $1 Started.
    else
        kill $!
        echo $1 Error!
    fi
}

if [ $# -lt 1 ]; then
    echo Usage: challenge path/to/opponent [path/to/map]
fi

if [ $# -eq 2 ]; then
    export AICMap=$2
fi

java -jar server/flowsgameserver-v2.0.jar &
server_pid=$!
check_last_command Server
read -p 'Press Enter to run clients...' wait
$1 &
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
