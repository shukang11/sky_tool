import os
import app
import unittest
import tempfile
import json

class test_upload(unittest.TestCase):

    def setUp(self):
        cur_app = app.create_app('development')
        self.db_fd, cur_app.config["DATABASE"] = tempfile.mkstemp()
        cur_app.config["TESTING"] = True
        self.app = cur_app.test_client()
        app.db.init_app(cur_app)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config["DATABASE"])

    def test_empty_file_list(self):
        rv = self.app.get('/api/v1000/file/list')
        resp = rv.data.decode()
        data = json.loads(resp)
        self.assertIsNotNone(data)

    def test_not_upload(self):
        rv = self.app.post("/api/v1000/upload", data=dict(
            files=[]
        ), follow_redirects=True)
        resp = rv.data.decode()
        data = json.loads(resp)
        self.assertIsNotNone(data["body"])
        self.assertEqual(data["code"], 0)
        self.assertIsNotNone(data["toast"])

    def test_upload(self):
        from io import StringIO
        f = StringIO()
        f.seek(0)
        f.name = 'hello.txt'
        files = {'files': [f]}
        rv = self.app.post("/api/v1000/upload", data=files, follow_redirects=True)
        resp = rv.data.decode()
        data = json.loads(resp)
        self.assertIsNotNone(data["body"])
        self.assertEqual(data["code"], 1)
        self.assertIsNotNone(data["toast"])
