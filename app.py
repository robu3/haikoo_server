from flask import Flask, escape, request
import json, logging, logging.handlers
from haikoo.haikoo import Haikoo, ImageDescriber
from haikoo_server.event_handler import EventHandler

app = Flask(__name__)

# simply log any incoming webhooks for debugging
webhook_logger = logging.getLogger("webhook_log")
file_handler = logging.handlers.RotatingFileHandler("webhook.log", maxBytes=32000, backupCount=5)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(name)s:\t%(message)s"))
webhook_logger.addHandler(file_handler)
webhook_logger.setLevel(logging.DEBUG)
app.webhook_logger = webhook_logger

# routing
@app.route("/")
def hello():
	name = request.args.get("name", "World (default)")
	return f"Hello, {escape(name)}!"

@app.route("/events", methods=["POST"])
def events():
	# webhook events will received here
	handler = EventHandler()
	handler.handle(request.json)

	return "OK"

@app.route("/log", methods=["POST"])
def log():
	app.webhook_logger.debug(f"Incoming webhook:\n{json.dumps(request.json, sort_keys=True, indent=4)}")
	return "OK"

