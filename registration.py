
import math
import toml
import getch

from assistants import *
from datetime import datetime, timedelta, date

# Read all calendar events from toml file
cal = toml.load("calendar.toml")

def registrate():
	if date.today().strftime('%d') != "12":
		err("Today isn't work hour day registration things and stuff", False)

	if int(date.today().strftime('%d')) >= 12:
		tupmon = (int(date.today().strftime('%m')) - 1, int(date.today().strftime('%m')))
	else:
		tupmon = (int(date.today().strftime('%m')), int(date.today().strftime('%m')) + 1)

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

if __name__ == '__main__':
	try:
		registrate()
	except KeyboardInterrupt:
		# Show this instead of error on KeyboardInterrupt
		err("Goodbye..")

