#!/bin/bash

python -m uvicorn app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 5480 &
app_pid=$!
echo "app_pid: $app_pid"

python -m app.worker.main_vector &
vector_pid=$!
echo "vector_pid: $vector_pid"

python -m app.worker.main_video_comment &
video_pid=$!
echo "video_pid: $video_pid"

while true; do
    wait -n -p died_pid
    echo "进程 $died_pid 退出了"

    case $died_pid in
        $app_pid)
            echo "重启 app"
            python -m uvicorn app.main:app \
                --reload \
                --host 0.0.0.0 \
                --port 5480 &
            app_pid=$!
            ;;
        $vector_pid)
            echo "重启 vector"
            python -m app.worker.main_vector &
            vector_pid=$!
            ;;
        $video_pid)
            echo "重启 video"
            python -m app.worker.main_video_comment &
            video_pid=$!
            ;;
    esac
done