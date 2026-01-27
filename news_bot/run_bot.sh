#!/bin/bash
# 新闻机器人启动脚本

cd "$(dirname "$0")"

# 设置环境变量避免权限问题
export HOME=/tmp
export PYTHONDONTWRITEBYTECODE=1
export TMPDIR=/tmp

# 运行Python程序
/usr/bin/python3 test_run.py "$@"
