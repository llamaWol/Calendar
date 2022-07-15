
import os
import sys
import toml
import uuid
import getch

from assistants import Msg, valid

from datetime import datetime, timedelta

# Read existing events and locations from toml files
calendar = toml.load("calendar.toml")
locations = toml.load("locations.toml")

datefmt = "%d/%m/%Y"

today = datetime.today()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)

def evnew(day, err = None):
	if err:
		Msg.err(err)

	name = Msg.ask("What calendar does this event belong to?").lower()
	if name == "": return evnew(day, "Give a calendar for the event")

	title = Msg.ask("What do you want to call this event?").title()
	if title == "": return evnew(day, "Give the event a title")

	notes = Msg.ask("Any comments?")

	if title in locations:
		location = locations[title]
	else:
		location = Msg.ask("Where does this event take place?")
		if location != "":
			if not valid(location, "postal"):
				return evnew(day, f"{location} is not a valid postal code")

	starttime = Msg.ask("When does the event start?")
	if not valid(starttime, "time"): return evnew(day, f"{starttime} is not a valid time")

	endtime = Msg.ask("When does the event end?")
	if not valid(endtime, "time"): return evnew(day, f"{endtime} is not a valid time")

	# Create event id
	identifier = str(uuid.uuid4().fields[-1])[:8]

	# Create event, if calendar doesn't exist, create it as well
	try:
		calendar[name][identifier] = {
			"title": title,
			"notes": notes,
			"location": location,
			"date": day,
			"from": starttime,
			"to": endtime
		}
	except KeyError:
		calendar[name] = {
			"colour": 0
		}
		calendar[name][identifier] = {
			"title": title,
			"notes": notes,
			"location": location,
			"date": day,
			"from": starttime,
			"to": endtime
		}

	Msg.suc(f"Added event to calendar. (id: {identifier})")
	Msg.say("b - back   q - quit")
	while True:
		try:
			key = getch.getch()
			# If pressed key is B, go back to main function
			if key == "b":
				return main(day)
			# If pressed key is Q, quit program
			elif key == "q":
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

def evedit(day):

	Msg.say("b - back   q - quit")
	while True:
		try:
			key = getch.getch()
			# If pressed key is B, go back to main function
			if key == "b":
				return main(day)
			# If pressed key is Q, quit program
			elif key == "q":
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

def evremove(day, err = None):
	if err:
		Msg.err(err)

	req = Msg.ask("What's the id of the event?")
	if not valid(req, "id"): return evremove(day, f"{req} is not a valid id")

	found = False
	for name in calendar:
		for event in calendar[name]:
			if event == req:
				del calendar[name][event]
				found = True
				Msg.suc(f"Removed event from calendar. (id: {req})")
				break

	if not found: return evremove(day, f"Couldn't find event with id {req}")

	Msg.say("b - back   q - quit")
	while True:
		try:
			key = getch.getch()
			# If pressed key is B, go back to main function
			if key == "b":
				return main(day)
			# If pressed key is Q, quit program
			elif key == "q":
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

def work(day, month = None):

	Msg.say("b - back   q - quit")
	while True:
		try:
			key = getch.getch()
			# If pressed key is B, go back to main function
			if key == "b":
				return main(day)
			# If pressed key is Q, quit program
			elif key == "q":
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

def main(day = None):
	if not day:
		day = today.strftime(datefmt)

	dtobj = datetime.strptime(day, datefmt)

	os.system('clear')
	# Print date of day you're viewing
	print(f"\nDate \033[33m{day}\033[0m")

	something = False
	for name in calendar:
		colour = 32 if dtobj < yesterday else calendar[name]["colour"]
		for event in calendar[name]:
			if event == "colour": continue
			if calendar[name][event]["date"] == day:
				something = True
				Msg.eprint(event, calendar[name][event], colour)

	if colour != 32: colour = 0
	if not something:
		print(f"\n\033[{colour}mNothing happening this day")

	Msg.say("j - prev day   k - next day   g - go to day   t - today   n - new event   e - edit event   r - remove event   w - working hours   q - quit")
	while True:
		try:
			key = getch.getch()
			# If pressed key is J, go to previous day
			if key == "j":
				newday = dtobj - timedelta(days=1)
				return main(newday.strftime(datefmt))
			# If pressed key is K, go to next day
			elif key == "k":
				newday = dtobj + timedelta(days=1)
				return main(newday.strftime(datefmt))
			# If pressed key is G, go to mentioned day
			elif key == "g":
				newday = Msg.ask("What day do you want to go to?")
				# Check if yesterday, today or tomorrow
				if newday == "yesterday":
					newday = yesterday.strftime(datefmt)
				elif newday == "today":
					newday = today.strftime(datefmt)
				elif newday == "tomorrow":
					newday = tomorrow.strftime(datefmt)
				# Otherwise check if given date is valid, or else exit
				else:
					if not valid(newday, "date"): 
						return main()

				return main(newday)
			# If pressed key is T, go to today
			elif key == "t":
				if today.strftime(datefmt) != day:
					return main()
			# If pressed key is N, add a new event on selected day
			elif key == "n":
				return evnew(day)
			# If pressed key is E, edit an event by id
			elif key == "e":
				return evedit(day)
			# If pressed key is R, remove an event by id
			elif key == "r":
				return evremove(day)
			# If pressed key is W, show work hours of current month
			elif key == "w":
				return work(day)
			# If pressed key is Q, quit program
			elif key == "q":
				sys.exit()
		except KeyboardInterrupt:
			sys.exit()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.exit()
	except Exception as error:
		Msg.err(f"An unexpected error has occured:\n{error}")
	finally:
		# Write calendar to toml file
		with open("calendar.toml", "w") as file:
			toml.dump(calendar, file)

		Msg.suc("Succesfully ran this very awesome program :)")