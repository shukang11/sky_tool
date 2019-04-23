import re

class TestRe(object):
    def test_re001(self):
        descript = """
        <p>dfasdfs</p>
        """
        html_rex = r'<.*>.*?</.*>'
        result = re.match(html_rex, descript)
        assert result != None
