
import os
import sys
import toml
import uuid

from assistants import *
from datetime import datetime, timedelta, date

# Read existing calendar events from toml file
cal = toml.load("calendar.toml")
loc = toml.load("locations.toml")

# Show all events on given date
def showEvents(day = None):
	# Find out when yesterday was (Hint: Probably the day before today)
	yesterday = datetime.today() - timedelta(days=1)

	# If no day is given, use today
	if not day:
		day = date.today().strftime('%d/%m/%Y')

	# Create datetime object
	obj = datetime.strptime(day, "%d/%m/%Y")

	os.system('clear')
	# Print date of day you're viewing
	print(f"\nDate \033[33m{day}\033[0m")

	something = False
	# Loop through all calendars and events
	for c in cal:
		# Set colour to green if event has happened, otherwise to the colour of the calendar
		clr = 32 if obj < yesterday else cal[c]["colour"]
		for event in cal[c]:
			if event == "colour": continue
			if cal[c][event]["date"] == day:
				something = True
				eprint(event, cal[c][event], clr)

	# Reset colour if it's not green 
	if clr != 32: clr = 0
	if not something:
		print(f"\n\033[{clr}mNothing happening this day")


	say("j - Prev day   k - Next day   n - Today   f - Go to day")
	# Listen for keypresses
	while True:
		try:
			key = getch.getch()
			# If pressed key is J, go to previous day
			if key == "j":
				newday = obj - timedelta(days=1)
				showEvents(str(newday.strftime("%d/%m/%Y")))
				break
			# If pressed key is J, go to next day
			elif key == "k":
				newday = obj + timedelta(days=1)
				showEvents(str(newday.strftime("%d/%m/%Y")))
				break
			# If pressed key is F, go to mentioned day
			elif key == "f":
				newday = ask("What day?")
				# Check if yesterday, today or tomorrow
				if newday == "yesterday":
					foo = date.today() - timedelta(days=1)
					newday = foo.strftime('%d/%m/%Y')
				elif newday == "today":
					newday = date.today().strftime('%d/%m/%Y')
				elif newday == "tomorrow":
					foo = date.today() + timedelta(days=1)
					newday = foo.strftime('%d/%m/%Y')
				# Otherwise check if given date is valid, or else exit
				else:
					if not valid(newday, "date"): sys.exit()

				showEvents(newday)
				break
			# If pressed key is N, go to today
			elif key == "n":
				if date.today().strftime('%d/%m/%Y') == day: continue
				showEvents()
				break
			# Exit if pressed key isnt any of the above
			else:
				break
		# Exit peacefully on KeyboardInterrupt
		except KeyboardInterrupt:
			sys.exit()

def workHours():
	if date.today().strftime('%d') != "12":
		err("Today isn't work hour day registration things and stuff")

	month = ask("Of what month do you want to know the stuff?").lower()
	if month == "current":
		if int(date.today().strftime('%d')) >= 12:
			tupmon = (int(date.today().strftime('%m')) - 1, int(date.today().strftime('%m')))
		else:
			tupmon = (int(date.today().strftime('%m')), int(date.today().strftime('%m')) + 1)
	else:
		months = {"dec/jan": (12, 1),"jan/feb": (1, 2),"feb/mar": (2, 3),"mar/apr": (3, 4),"apr/mei": (4, 5),"mei/jun": (5, 6),"jun/jul": (6, 7),"jul/aug": (7, 8),"aug/sep": (8, 9),"sep/okt": (9, 10),"okt/nov": (10, 11),"nov/dec": (11, 12)}
		if not month in months: err("Input a valid month", True)
		tupmon = months[month]

	if tupmon[0] == 12:
		start = datetime.strptime(f"13/{tupmon[0]}/{date.today().year - 1}", "%d/%m/%Y")
	else:
		start = datetime.strptime(f"13/{tupmon[0]}/{date.today().year}", "%d/%m/%Y")

	if tupmon[1] == 13:
		end = datetime.strptime(f"12/01/{date.today().year + 1}", "%d/%m/%Y")
	else:
		end = datetime.strptime(f"12/{tupmon[1]}/{date.today().year}", "%d/%m/%Y")

	# Set default values
	total = 0
	days_worked = 0
	# Loop through every event in work calendar
	for event in cal["work"]:
		# Get event date
		day = datetime.strptime(cal["work"][event]["date"], "%d/%m/%Y")

		# Check if event date is in between start and end date
		if start <= day <= end:
			days_worked += 1
			# Default value for breaks (1h)
			breaks = 60

			# The time the event starts and ends
			starttime = datetime.strptime(cal["work"][event]["from"], "%H:%M")
			endtime = datetime.strptime(cal["work"][event]["to"], "%H:%M")

			# Check if you haven't had breaks
			if starttime >= time("10:00"):
				breaks -= 15
			if starttime >= time("12:00"):
				breaks -= 30
			if starttime >= time("15:00"):
				breaks -= 15

			if endtime <= time("15:00"):
				breaks -= 15
			if endtime <= time("13:00"):
				breaks -= 30

			# Get amount of hours and minutes I've worked
			hrs, mins, _ = str(endtime - starttime - timedelta(minutes=breaks)).split(":")
			# Convert minutes to decimal
			mins = truncate(int(mins) * 0.01675, 2)

			print(f"{cal['work'][event]['date']}\t\t-> {int(hrs) + mins}")
			# Add time to total
			total += int(hrs) + mins

	print(f"\nTotaal aantal uren\t-> {total}")
	print(f"Dagen gewerkt\t\t-> {days_worked}")
	print(f"Salaris\t\t\t-> {truncate(total * 3.9, 2)}")

	say("Press any key to go back  –  ctrl + c to quit")
	while True:
		try:
			res = getch.getch()
			break
		# Exit peacefully on KeyboardInterrupt
		except KeyboardInterrupt:
			sys.exit()

# Add an event to said calendar
def addEvent():
	calendar = ask("What calendar does this event belong to?").lower()
	if calendar == "": err("Input a calendar for the event.", True)
	
	title = ask("What do you want to call this event?").title()
	if calendar == "": err("Make sure you give the event a title", True)
	notes = ask("Any comments?")

	# Check if title is a known location
	if title in loc:
		location = loc[title]
	# Otherwise ask for a postal code
	else:
		location = ask("Where does this event take place?")
		if location != "": 
			if not valid(location, "postal"): 
				err("Input a valid postal code.", True)
	
	day = ask("What date does the event happen")
	if day == "today":
		day = date.today().strftime('%d/%m/%Y')
	elif day == "tomorrow":
		day = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
	if not valid(day, "date"): err("Input a valid date.", True)
	
	starttime = ask("When does it start")
	if not valid(starttime, "time"): err("Input a valid time.", True)
	
	endtime = ask("When does it end")
	if not valid(endtime, "time"): err("Input a valid time.", True)

	# Create event id
	identifier = str(uuid.uuid4().fields[-1])[:8]

	try:
		cal[calendar][identifier] = {
			"title": title,
			"notes": notes,
			"location": location,
			"date": day,
			"from": starttime,
			"to": endtime
		}
	except KeyError: # If calendar doesn't exist, create it
		cal[calendar] = {}
		cal[calendar][identifier] = {
			"title": title,
			"notes": notes,
			"location": location,
			"date": day,
			"from": starttime,
			"to": endtime
		}

	suc(f"Added event to calendar. (id: {identifier})")
	say("Press any key to go back  –  ctrl + c to quit")
	while True:
		try:
			res = getch.getch()
			break
		# Exit peacefully on KeyboardInterrupt
		except KeyboardInterrupt:
			sys.exit()

def rmEvent():
	req = ask("What's the id of the event?")
	if not valid(req, "id"): err("Input a valid id.", True)

	for c in cal:
		for event in cal[c]:
			if event == req:
				del cal[c][event]
				suc(f"Removed event from calendar. (id: {req})")
				break

	say("Press any key to go back  –  ctrl + c to quit")
	while True:
		try:
			res = getch.getch()
			break
		# Exit peacefully on KeyboardInterrupt
		except KeyboardInterrupt:
			sys.exit()

# First function to be run, ask what you want to do
def init():
	action = choice("What do you want to do?\n1. Show all events\n2. Add event\n3. Remove event\n4. See work hours")
	if action == "1":
		showEvents()
	elif action == "2":
		addEvent()
	elif action == "3":
		rmEvent()
	elif action == "4":
		workHours()
	else:
		err("Thats not a valid option", True)


if __name__ == '__main__':
	try:
		init()
		# Write calendar to toml file
		with open("calendar.toml", "w") as v:
			toml.dump(cal, v)

		# Restart script
		os.system('clear')
		os.execv(sys.executable, ['python3'] + sys.argv)
	except KeyboardInterrupt:
		# Exit peacefully on KeyboardInterrupt
		err("Joost doesn't want you to go :(")