#!/bin/bash

# 1. 切换到你的项目根目录 (包含 manage.py 的目录)
cd /home/aFatOtaku/newTravel/mydearweb || exit

# 2. 激活你的虚拟环境 (根据你之前的报错，你的环境在 venv)
source /home/aFatOtaku/newTravel/venv/bin/activate

# 3. 执行 Python 清理脚本，并将日志输出到 clean_log.txt 里
python clean_temps.py >> /home/aFatOtaku/newTravel/mydearweb/clean_log.txt 2>&1