# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:lupengliang
import os

import yaml

class ReadConfig:

    def __init__(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(os.path.dirname(current_path), 'config/config.yaml')

    # 读取参数文件
    def get_data(self):
        with open(self.config_path, encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    # 获取盘符
    @classmethod
    def get_drive(cls, path):
        return path[:2]


data = ReadConfig().get_data()
# 启动结构
drive = ReadConfig.get_drive(path=data.get('path').get('game_path'))
# mysql
myUsername = str(data.get("mysql").get("username"))
myPassword = str(data.get("mysql").get("password"))
myIp = str(data.get("mysql").get("ip"))
myPort = data.get("mysql").get("port")
myDatabase = data.get("mysql").get("databases")

# ob
obUsername = str(data.get("ob").get("username"))
obPassword = str(data.get("ob").get("password"))
obIp = str(data.get("ob").get("ip"))
obPort = data.get("ob").get("port")
obDatabase = data.get("ob").get("databases")


if __name__ == '__main__':
    print(type(myPassword))
    print(type(myPort))
