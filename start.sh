#!/bin/bash

# B站NLP分析系统启动脚本 (简化版)
# 使用固定路径: /home/vscode/MyCode/project/bilibili_NLP/python3.12_env/bin
# 端口: 5480

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 固定路径配置
PYTHON_ENV_PATH="/home/vscode/MyCode/project/bilibili_NLP/python3.12_env/bin"
PROJECT_PATH="/home/vscode/MyCode/project/bilibili_NLP"
PORT=5480

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  B站NLP分析系统启动脚本 (简化版)${NC}"
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}Python环境: $PYTHON_ENV_PATH${NC}"
    echo -e "${BLUE}项目路径: $PROJECT_PATH${NC}"
    echo -e "${BLUE}端口: $PORT${NC}"
    echo -e "${BLUE}================================${NC}"
}

# 检查Python环境
check_python_env() {
    print_message "检查Python环境..."
    if [ ! -f "$PYTHON_ENV_PATH/python" ]; then
        print_error "Python环境不存在: $PYTHON_ENV_PATH/python"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_ENV_PATH/python --version 2>&1)
    print_message "Python版本: $PYTHON_VERSION"
}

# 检查项目路径
check_project_path() {
    print_message "检查项目路径..."
    if [ ! -d "$PROJECT_PATH" ]; then
        print_error "项目路径不存在: $PROJECT_PATH"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_PATH/backend/main.py" ]; then
        print_error "main.py文件不存在: $PROJECT_PATH/backend/main.py"
        exit 1
    fi
    
    print_message "项目路径检查通过"
}

# 检查端口占用
check_port() {
    print_message "检查端口 $PORT 是否被占用..."
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口 $PORT 已被占用"
        print_error "请先停止占用端口 $PORT 的进程，或修改脚本中的端口号"
        exit 1
    else
        print_message "端口 $PORT 可用"
    fi
}

# 启动后端服务
start_backend() {
    print_message "启动后端服务..."
    print_message "服务地址: http://0.0.0.0:$PORT"
    print_message "API文档: http://0.0.0.0:$PORT/docs"
    print_message "按 Ctrl+C 停止服务"
    echo
    
    # 切换到项目目录并启动服务
    cd "$PROJECT_PATH/backend"
    $PYTHON_ENV_PATH/python -m uvicorn main:app --host 0.0.0.0 --port $PORT --reload
}

# 清理函数
cleanup() {
    print_message "正在停止服务..."
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    print_header
    
    # 执行检查
    check_python_env
    check_project_path
    check_port
    
    # 启动服务
    start_backend
}

# 运行主函数
main "$@" 