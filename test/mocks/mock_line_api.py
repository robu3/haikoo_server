from unittest.mock import Mock
from test.mocks.mock_response import MockResponse

class MockLineApi:
	"""
	A mock LINE API for use in unit testing.
	"""

	def __init__(self, content_path=None):
		self.content_path = content_path

	def reply_message(self, token, msg):
		"""
		"Replies" by printing the message in the console.
		"""

		print(msg)

	def iter_content(self):
		if self.content_path is not None:
			with open(self.content_path, "rb") as f:
				while True:
					chunk = f.read(1024)
					yield chunk

					if not chunk:
						break

		else:
			for i in range(8):
				yield bytearray(1024)

	def get_message_content(self, msg_id):
		content = Mock()
		content.response = MockResponse(
			status_code=200,
			headers={ "Content-Type": "image/png" }
		)
		content.iter_content = self.iter_content

		return content