from tests import TestBase


class TestTodo(TestBase):

    def test_addtodo(self):
        test_add_title = "test_add_title"
        token = self.login()
        params = {
            "title": test_add_title,
            "token": token
        }
        rv = self._client.post("/api/v1000/todo/add", json=params)
        assert rv.status_code == 200
        assert rv.json["todo_id"] != ""

    def get_todo(self, title):
        test_add_title = title
        token = self.login()
        params = {
            "title": test_add_title,
            "token": token
        }
        rv = self._client.post("/api/v1000/todo/add", json=params)
        assert rv.status_code == 200
        assert rv.json["todo_id"] != ""
        return (token, rv.json["todo_id"])

    def test_finishtodo(self):
        token, todo_id = self.get_todo("test_finish_todo")
        rv = self._client.post("/api/v1000/todo/finish", json={
            "todo_id": todo_id,
            "token": token
        })
        assert rv.status_code == 200
        assert rv.json["todo_id"] == todo_id
        assert rv.json["todo_state"] == 2

    def test_undotodo(self):
        token, todo_id = self.get_todo("test_undo_title")
        rv = self._client.post("/api/v1000/todo/undo", json={
            "todo_id": todo_id,
            "token": token
        })
        assert rv.status_code == 200
        assert rv.json["todo_id"] == todo_id
        assert rv.json["todo_state"] == 1

    def test_removetodo(self):
        token, todo_id = self.get_todo("test_remove_title")
        rv = self._client.post("/api/v1000/todo/remove", json={
            "todo_id": todo_id,
            "token": token
        })
        assert rv.status_code == 200
        assert rv.json["todo_id"] == todo_id
        assert rv.json["todo_state"] == 3
