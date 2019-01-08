# response wrapper

class RespObj:
    statusCode: int
    body: any
    toast: str

    def __init__(self, code=1, body=None, toast=""):
        self.statusCode = code
        self.body = body
        self.toast = toast

    def json(self):
        j = {
            "code": self.statusCode,
            "body": self.body,
            "toast": self.toast
        }
        return j

    def __str__(self):
        """
        String representation of the class instance.

        :return:
        """
        return 'Resp {{code}, {body}, {toast}}'.format(
            code=self.statusCode,
            body=self.body,
            toast=self.toast
        )

    def __repr__(self):
        return self.__str__()