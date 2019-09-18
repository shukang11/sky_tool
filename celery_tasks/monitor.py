# -*- coding: utf-8 -*-

import re
import os
import time
import threading

def exec_cmd(command) -> str:
    r = os.popen(command)
    text = r.read()
    r.close()
    return text

def disk_state():
    """
    磁盘空间监控
    """
    command = "df -h"
    result = exec_cmd(command)
    values = result.strip().split("\n")
    disk_lists = []
    for value in values:
        disk_lists.append(value.strip().split())
    for disk in disk_lists[1:]:
        print("\t文件系统：{name} \t容量：{size} \t已用：{used} \t可用：{unused} \t已用%挂载点：{c}".format(name=disk[0], size=disk[1], used=disk[2], unused=disk[3], c=disk[4]))

if __name__ == "__main__":
    disk_state()