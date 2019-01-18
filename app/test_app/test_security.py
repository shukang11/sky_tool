#  @author: treee
#
#  @contact: 2332532718@qq.com
#
#  @file: test_security.py
#
#  @time: 2019-01-18 17:58
#

import unittest
from app.utils import login_require
from flask import request
from main import app


class TestSecurity(unittest.TestCase):

    def test_index(self):
        with app.test_request_context("/api/v1000/help"):
            print(request.values)
        pass
