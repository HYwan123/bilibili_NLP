#!/bin/bash

# --- 信号处理：确保按下 Ctrl+C 时杀死所有后台子进程 ---
cleanup() {
    echo ""
    echo "正在停止所有分析服务..."
    [ -n "$app_pid" ] && kill $app_pid 2>/dev/null
    [ -n "$vector_pid" ] && kill $vector_pid 2>/dev/null
    [ -n "$video_pid" ] && kill $video_pid 2>/dev/null
    echo "清理完成，已退出。"
    exit 0
}

trap 'cleanup' SIGINT SIGTERM

# 启动后端 API 服务
echo "正在启动后端接口 (Port: 5480)..."
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 5480 &
app_pid=$!
echo "APP PID: $app_pid"

# 启动向量处理 Worker
echo "正在启动向量数据库同步服务..."
python -m app.worker.main_vector &
vector_pid=$!
echo "VECTOR PID: $vector_pid"

# 启动评论分析 Worker
echo "正在启动评论智能分析服务..."
python -m app.worker.main_video_comment &
video_pid=$!
echo "VIDEO PID: $video_pid"

echo "-----------------------------------"
echo "服务已全部启动。按下 Ctrl+C 可安全关闭。"
echo "-----------------------------------"

# 持续监听进程状态
while true; do
    # 检查进程是否还在运行
    if ! kill -0 $app_pid 2>/dev/null; then
        echo "警告: 后端 API 服务已意外停止。"
    fi
    if ! kill -0 $vector_pid 2>/dev/null; then
        echo "警告: 向量同步服务已意外停止。"
    fi
    if ! kill -0 $video_pid 2>/dev/null; then
        echo "警告: 评论分析服务已意外停止。"
    fi
    
    sleep 5
done
