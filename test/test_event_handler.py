import unittest, json, os, shutil
from haikoo_server.event_handler import EventHandler
from test.mocks.mock_line_api import MockLineApi
from linebot.models import ImageSendMessage

class EventHandlerTest(unittest.TestCase):
	PROCESSING_DIR = "test/processing/"

	def build_request(self, event_type):
		# build mock request w/ body

		# load body content from fixture
		# and add to request object
		with open("./test/fixtures/" + event_type + ".json") as f:
			body = json.loads(f.read())

		return body

	def test_generate_haiku(self):
		handler = EventHandler(self.PROCESSING_DIR)

		# copy test file for manipulation
		source_image = "test/fixtures/image.jpeg"

		# generate haiku
		images = handler.generate_haiku(source_image)

		self.assertTrue(os.path.exists(images[0]))
		self.assertTrue(os.path.exists(images[1]))

		os.remove(images[0])
		os.remove(images[1])

	def test_format_message_image(self):
		handler = EventHandler(self.PROCESSING_DIR)
		msg = handler.format_message_image("test/fixtures/image.jpeg", "test/fixtures/image_thumb.jpeg")

		print(msg)
		self.assertIsNot(msg, None)

		msg_json = msg.as_json_dict()
		self.assertEqual(msg_json["originalContentUrl"], "https://haikoo.bit-noodle.com/images/image.jpeg")
		self.assertEqual(msg_json["previewImageUrl"], "https://haikoo.bit-noodle.com/images/image_thumb.jpeg")

	def test_fetch_line_content(self):
		# build mock request and fetch content
		request = self.build_request("message_image")

		handler = EventHandler(self.PROCESSING_DIR, line_api=MockLineApi(content_path="test/fixtures/image.jpeg"))
		message_id = request["events"][0]["message"]["id"]
		filename = handler.fetch_line_content(message_id)

		# content should have been fetched
		self.assertTrue(os.path.exists(filename))
		os.remove(filename)

	def test_handle(self):
		# integration test: build mock request and handle it
		request = self.build_request("message_image")
		handler = EventHandler(self.PROCESSING_DIR, line_api=MockLineApi(content_path="test/fixtures/image.jpeg"))
		handler.image_root_url = self.PROCESSING_DIR
		message_id = request["events"][0]["message"]["id"]

		reply_msg = handler.handle(request)

		print(reply_msg)
		self.assertIsNot(reply_msg, None)
		self.assertIsNot(reply_msg.original_content_url, None)
		self.assertTrue(os.path.exists(reply_msg.original_content_url))
		self.assertTrue(os.path.exists(reply_msg.preview_image_url))

		# confirm that the content was fetched and the haiku images were generated
		os.remove(reply_msg.original_content_url)
		os.remove(reply_msg.preview_image_url)
		os.remove(os.path.join(self.PROCESSING_DIR, message_id + ".png"))


