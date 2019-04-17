from tests import TestBase

class TestRss(TestBase):

    def test_add_rss(self):
        rss_link = "https://www.zhihu.com/rss"
        token = self.login()
        params = {
            "source": rss_link,
            "token": token
        }
        rv = self._client.post("/api/rss/add", json=params)
        assert rv.status_code == 200
        assert rv.json["rss_id"] != None

    def test_list_rss(self):
        token = self.login()
        params = {
            "token": token
        }
        rv = self._client.post("/api/rss/limit", json=params)
        assert rv.status_code == 200

    def test_list_rss_content(self):
        token = self.login()
        params = {
            "token": token
        }
        rv = self._client.post("/api/rss/content/list", json=params)
        assert rv.status_code == 200

    def test_re001(self):
        import re
        descript = """
        <p>dfasdfs</p>
        """
        html_rex = r'<.*>(.*?)</.*>'
        result = re.match(p7, c7)
        assert result != None