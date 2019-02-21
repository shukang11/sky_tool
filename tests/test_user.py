import sys
from os import path

from flask import Flask
import pytest
# 将路径添加到 sys.path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from app import create_app
from app.utils import getmd5

@pytest.fixture("module")
def app():
    app = create_app('testing')
    yield app

@pytest.fixture("module")
def client(app):
    return app.test_client()


class TestUser(object):
    def setup_method(self):
        self._email = "123456789@qq.com"
        self._password = getmd5("123456")

    def test_register_on_error(self, client):
        password = getmd5("123456")
        rv = client.post("/api/v1000/user/register", json={
            "email": self._email,
            "password": password
        })

        password = getmd5("123456")
        rv = client.post("/api/v1000/user/register", json={
            "email": self._email,
            "password": password
        })
        assert rv.status_code == 400

    def test_login(self, client) -> str:
        rv = client.post("/api/v1000/user/login", json={
            "email": self._email,
            "password": self._password
        })
        assert rv.status_code == 200
        return rv.json["token"]

    def test_user_info(self, client):
        token = self.test_login(client)
        rv = client.post("/api/v1000/user/info", json={
            "token": token
        })
        assert rv.status_code == 200
        assert rv.json["email"] == self._email
        assert rv.json["token"] == token
        
    def test_nickname(self, client):
        token = self.test_login(client)
        test_nickname = "test_nickname"
        rv = client.post("/api/v1000/user/nickname", json={
            "token": token,
            "nickname": test_nickname
        })
        assert rv.status_code == 200
        assert rv.json["nickname"] == test_nickname
        assert rv.json["token"] == token
        assert rv.json["email"] == self._email
        rv =client.get("/api/v1000/user/nickname", json={
            "token": token
        })
        assert rv.status_code == 200
        assert rv.json["nickname"] == test_nickname