#!/bin/bash

# 进入项目目录
cd /home/aFatOtaku/newTravel/mydearweb || exit

# 激活虚拟环境
source /home/aFatOtaku/newTravel/venv/bin/activate

# 执行清理脚本，并将日志输出到 clean_iot.log
python clean_iot_data.py >> /home/aFatOtaku/newTravel/mydearweb/clean_iot.log 2>&1