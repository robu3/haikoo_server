import json, re, os, urllib.parse
from linebot import LineBotApi
from linebot.models import ImageSendMessage
from linebot.exceptions import LineBotApiError
from haikoo.haikoo import Haikoo, ImageDescriber

class EventHandler:
	"""
	Handles LINE webhook events.
	"""

	MIME_TYPE_MAP = {
		"image/jpeg": "jpg",
		"image/png": "png",
		"image/gif": "gif"
	}

	def __init__(self, processing_dir = None, line_api = None):
		# configure event handling
		self.event_router = {
			"message": self.handle_message
		}

		# load configuration options from config file
		try:
			with open("config.json") as f:
				self.config = json.loads(f.read())
		except:
			print("Missing or invalid configuration file: config.json")
			self.config = {}

		if "cv_key" not in self.config or "cv_region" not in self.config:
			print("Config file must contain 'cv_key' and 'cv_region' settings.")
			exit()

		# set the processing directory
		# use the config value if constructor was not provided a value
		if processing_dir is None:
			if "processing_dir" in self.config:
				self.processing_dir = self.config["processing_dir"]
			else:
				self.processing_dir = "."
		else:
			self.processing_dir = processing_dir

		if not os.path.exists(self.processing_dir):
			os.makedirs(self.processing_dir)

		# set image URL root and LINE API implementation
		self.image_root_url = self.config["image_root_url"]

		if line_api is None:
			self.line_api = LineBotApi(self.config["line_channel_token"])
		else:
			self.line_api = line_api

	"""
	Handles a web hook request.
	Each request message may contain multiple events that will need to be handled.
	
	:return: The LINE message sent in reply (if applicable).
	"""
	def handle(self, request):
		# handle each event in the request in order
		for event in request["events"]:
			if event["type"] in self.event_router:
				# event we can handle
				# TODO: try/except here?
				reply_msg = self.event_router[event["type"]](event)

		return reply_msg

	def handle_message(self, event):
		msg = event["message"]
		reply_token = event["replyToken"]
		reply_msg = None

		# only handle line messages
		if msg["type"] == "image":
			if msg["contentProvider"]["type"] != "line":
				raise Exception("Unable to handle message type: " + msg["contentProvider"]["type"])

			# fetch binary data from content endpoint
			source_image = self.fetch_line_content(msg["id"])

			# generate the haiku
			haiku_images = self.generate_haiku(source_image)

			# and send the response
			reply_msg = self.format_message_image(haiku_images[0], haiku_images[1])
			self.line_api.reply_message(reply_token, reply_msg)
		else:
			print("Unable to handle type: " + msg["type"])

		return reply_msg

	def format_message_image(self, image, thumbnail):
		"""
		Formats a LINE image message.

		:return: A formatted LINE message to be sent.
		"""
		msg = ImageSendMessage(
			original_content_url = urllib.parse.urljoin(self.image_root_url, os.path.basename(image)),
			preview_image_url = urllib.parse.urljoin(self.image_root_url, os.path.basename(thumbnail))
		)

		return msg

	"""
	Returns the correct file extension to use for the specified MIME type.

	:return: The extension, e.g., "jpg" or "png".
	"""
	def get_file_extension(self, mime_type):
		match = re.match(r"image/(\w+)", mime_type)

		if match:
			return match.group(1)

		return "dat"

	"""
	Fetches the LINE content for the specified message by ID.

	:return: The relative path/filename of the file created.
	"""
	def fetch_line_content(self, message_id):
		message_content = self.line_api.get_message_content(message_id)

		if message_content.response.status_code == 200:
			# write file content to disk
			content_type = message_content.response.headers["Content-Type"]
			filename = f"{self.processing_dir}/{message_id}.{self.get_file_extension(content_type)}"

			with open(filename, "wb") as f:
				for chunk in message_content.iter_content():
					f.write(chunk)
		else:
			raise Exception("Error attempting to fetch content from the LINE API")

		return filename

	"""
	Generates a haiku from an image overlaid on said image. 

	:return: Tuple of generated image paths -- (haiku image, thumbnail).
	"""
	def generate_haiku(self, source_image):
		image_prefix = os.path.splitext(os.path.basename(source_image))[0]

		# generate haiku
		describer = ImageDescriber(self.config["cv_key"], self.config["cv_region"])

		haikoo = Haikoo(describer, "fusion")
		result = haikoo.create_image(source_image, os.path.join(self.processing_dir, image_prefix + "_haikoo.png"))

		# generate thumbnail
		thumbnail = haikoo.create_thumbnail(
				result.image,
				os.path.join(self.processing_dir, image_prefix + "_thumb.png"),
				256,
				256)

		return (result.image, thumbnail)

