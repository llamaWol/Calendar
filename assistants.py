
import re
import sys
import getch

from datetime import datetime

def valid(v, mode):
	if mode == "time":
		regex = r"^([01][0-9]|2[0-3]):([0-5][0-9])$"
	elif mode == "date":
		regex = r"^(?:(?:31(\/)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$"
	elif mode == "postal":
		regex = r"^(?:\d{4})(?:\w{2})$"
	elif mode == "id":
		regex = r"^\d{8}$"

	if re.match(regex, v):
		return True
	else:
		return False

def time(stamp):
	return datetime.strptime(stamp, "%H:%M")

def date(str):
	return datetime.strptime(str, "%d/%m/%Y")

def truncate(n, places):
    return int(n * (10 ** places)) / 10 ** places

class Msg:
	def eprint(id, event, colour):
		print(f"\n\033[1;{colour}m{event['title']} \033[0;{colour}m(\033[0m{id}\033[{colour}m)\033[0m")
		if event["notes"] != "":
			print(f"{event['notes']}")
		if event["location"] != "":
			print(f"{event['location']}")
		print(f"{event['from']} - {event['to']}")

	def err(msg):
		msg = msg.replace("\n", "\n  ")
		print(f'\n\033[31m✘\033[0m {msg}')

	def suc(msg):
		msg = msg.replace("\n", "\n  ")
		print(f'\n\033[32m✔\033[0m {msg}')

	def say(msg):
		msg = msg.replace("\n", "\n  ")
		print(f'\n\033[33m…\033[0m {msg}')

	def ask(msg):
		msg = msg.replace("\n", "\n  ")
		res = input(f'\033[35m?\033[0m {msg}\n  ').strip()
		return res