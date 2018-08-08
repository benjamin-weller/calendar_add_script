"""
Usage:
    calendarInterface.py write <date_time> <reminder_level>
    calendarInterface.py read [date] [number_limit]
"""

from __future__ import print_function
import datetime
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file as oauth_file, client, tools
from docopt import docopt
import pyperclip

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


def read(service_handler, date=datetime.datetime.utcnow().isoformat(), number_limit=10):
    # Call the Calendar API
    now = date + 'Z'  # 'Z' indicates UTC time
    # print('Getting the upcoming 10 events')
    events_result = service_handler.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=number_limit, singleEvents=True,
                                                  orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        # noinspection PyInterpreter
        start = event['start'].get('dateTime', event['start'].get('date'))
        # print(start, event['summary'])

def write(service_handler, maya_time, reminder_level=1):
    #I think that maya should handle both the date and the time????

if __name__ == '__main__':
    arguments = docopt(__doc__)

    service_handler = main()

    if arguments["write"]:
        write(service_handler, arguments["<date_time>"])
    else:
        # Must be a read
        # Figure out how to do the optional params???
        read(service_handler, arguments[], arguments[])




