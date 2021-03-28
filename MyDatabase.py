# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 14:07:49 2021
database
@author: Chyer
"""

import pymysql
class MyDatabase:
        db = None
        def __init__(self):
                self.connect()
                return
        def connect(self):
                self.db = pymysql.connect(
                                host = "43.128.7.176",
                                port = 3306,
                                user = "chyer",
                                passwd = "password",
                                db = "iems5722",
                                use_unicode = True,
                                charset = "utf8",
                        )
                self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
                self.db.commit()
                return