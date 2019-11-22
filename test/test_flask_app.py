import unittest, json, logging, os
from app import app

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.webhook_logger = logging.getLogger("webhook_log")
        app.webhook_logger.addHandler(logging.FileHandler("test.log", "w"))

        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_log(self):
        # send POST request to endpoint
        # pretty-print it so that our assertion will work later
        post_body = json.dumps({
            "id": 1,
            "foo": "bar"
        }, sort_keys=True, indent=4)

        res =self.app.post(
            "/log",
            data=post_body,
            content_type="application/json"
            )

        # request should be successful and logged
        self.assertEqual(200, res.status_code)
        self.assertTrue(os.path.exists("test.log"))

        with open("test.log") as f:
            log_text = f.read()

        print(log_text)
        self.assertTrue(post_body in log_text)


