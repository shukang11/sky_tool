import sys
from os import path

from flask import Flask
import pytest
# 将路径添加到 sys.path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from app import create_app

@pytest.fixture("module")
def app():
    app = create_app('testing')
    yield app

@pytest.fixture("module")
def client(app):
    return app.test_client()


def test_md5(client):
    rv = client.get("/api/v1000/tool/encryption/md5?source=123456")
    assert rv.status_code == 200
    assert rv.json["source"] == "123456"
    assert rv.json["type"] == "md5"
    assert rv.json["target"] == "e10adc3949ba59abbe56e057f20f883e"

def test_sha512(client):
    rv = client.get("/api/v1000/tool/encryption/sha512?source=123456")
    assert rv.status_code == 200
    assert rv.json["source"] == "123456"
    assert rv.json["type"] == "sha512"
    assert rv.json["target"] == "ba3253876aed6bc22d4a6ff53d8406c6ad864195ed144ab5c87621b6c233b548baeae6956df346ec8c17f5ea10f35ee3cbc514797ed7ddd3145464e2a0bab413"