# -*- coding: utf-8 -*-
'''
配置信息
https://github.com/benoitc/gunicorn/blob/master/examples/example_config.py
'''
__author__ = "tree_"
__copyright__ = "Copyright of tree_ (2019)."

import multiprocessing
import os

bind = '0.0.0.0:8091' # 绑定地址
workers =  1 
# 如果是正式环境需要根据实际情况开启线程数量
if os.environ.get('FLASK_ENV') == "production":
    bind = '0.0.0.0:6000' # 绑定地址
    workers =  multiprocessing.cpu_count() * 2 + 1 # 根据cpu数量指定线程数量