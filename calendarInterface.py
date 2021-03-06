"""
Usage:
    calendarInterface.py write <date_time> <title> [<reminder_level>]
    calendarInterface.py read [<date>]
"""

from __future__ import print_function
import datetime
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from docopt import docopt
import pyperclip
from tzlocal import get_localzone
import maya

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'


def main():
    """Shows basic usage of the Google Calendar API."""
    store = oauth_file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def read(service_handler, now=datetime.datetime.utcnow(), number_limit=10):
    # Call the Calendar API
    events_result = service_handler.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=number_limit, singleEvents=True,
                                                  orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        pyperclip.copy('No upcoming events found.')
        return
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        pyperclip.copy(pyperclip.paste()+f"\n{start} {event['summary']}")
        # print(start, event['summary'])


def write(service_handler, maya_time, title, reminder_level=1):
    # I'm giving maya assumes everything is UTC, and then asking it to keep that hour in utc except make it my time zone, this is backwards
    # I should make a date time in my current time zone at the time I ask for. I don't want to write a parser though
    event = {
        'summary': f"{title}",
        'description': '',
        'start': {
            # I've chosen to drop the UTC timezone after maya parses it
            'dateTime': f"{maya_time.datetime().replace(tzinfo=None).isoformat()}",
            'timeZone': f"{get_localzone()}",  # my timezone
        },
        'end': {
            'dateTime': f"{maya_time.datetime().replace(tzinfo=None).isoformat()}",
            'timeZone': f"{get_localzone()}",
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 24 * 60},  # a day before start
                {'method': 'popup', 'minutes': 60},  # 100 minutes before start
            ],
        },
    }

    event = service_handler.events().insert(
        calendarId='primary', body=event).execute()
    # print 'Event created: %s' % (event.get('htmlLink'))

if __name__ == '__main__':
    # TODO add repeat functionality
    # TODO add notification modification functionality
    # I want to add two optional parameters to write, the reminder level, and recurrence amount.
    # With that being said I don't think that I really care enough to add the command line option flags 
    # just to make this work. Additionally, I've tried to explain how this would complicate things below.
    # I'm going to leave the above todos, only because as of right now I call them from a .bat file.
    # this causes issues because I can't "polymorphically" defermine if I'm going to call with or without certain flags.

    arguments = docopt(__doc__)
    print(arguments)
    service_handler = main()

    if arguments["write"]:
        write(service_handler, maya.when(arguments["<date_time>"]), arguments["<title>"])
    else:
        # Must be a read
        read(service_handler, arguments.get("<date>"))