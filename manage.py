# coding=utf-8
"""
@version: 2017/12/19 019
@author: Suen
@contact: sunzh95@hotmail.com
@file: manage.py
@time: 11:40
@note:  ??
"""
from __future__ import unicode_literals

from flask_script import Manager
from app import create_app

app = create_app()
manager = Manager(app=app)

if __name__ == '__main__':
    manager.run()
