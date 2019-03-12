import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from app import create_app
from app.utils import getmd5

class TestBase(object):
    def setup_method(self):
        self._email = "123456789@qq.com"
        self._password = getmd5("123456")
        self._app = create_app("testing")
        self._client = self._app.test_client()

    def login(self) -> str:
        params = {
            "email": self._email,
            "password": self._password
        }
        rv = self._client.post("/api/user/login", json=params)
        print(params)
        assert rv.status_code == 200
        return rv.json["token"] or ""