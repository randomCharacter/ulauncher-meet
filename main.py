from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from typing import List
from meeting import Meeting

saved_meetings = []


def update_saved_meetings(meetings_string: str) -> List[Meeting]:
    global saved_meetings
    saved_meetings.clear()
    try:
        for meeting_pair in meetings_string.split(';'):
            meeting_pair = meeting_pair.split(':')
            name = meeting_pair[0]
            id = meeting_pair[1]
            saved_meetings.append(Meeting(name, id))
    except IndexError:
        saved_meetings = None


class MeetExtension(Extension):

    def __init__(self):
        super(MeetExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesLoadListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateListener())


class PreferencesLoadListener(EventListener):
    def on_event(self, event, extension):
        update_saved_meetings(event.preferences['saved_meetings'])


class PreferencesUpdateListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'shortcuts':
            update_saved_meetings(event.new_value)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        user_inputs = event.get_query().split()

        items = []

        if len(user_inputs) == 1 or user_inputs[1] in 'new':
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='New',
                                             description='Start new meeting',
                                             on_enter=OpenUrlAction('https://meet.google.com/new')))
        if len(user_inputs) > 1:
            meet_id = user_inputs[1]
            if saved_meetings is None:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name='Saved meetings misformed',
                                                 description='Please fix saved meetings in extension properties',
                                                 on_enter=DoNothingAction()))
            else:
                for meeting in saved_meetings:
                    if meet_id in meeting.name:
                        items.append(ExtensionResultItem(icon='images/icon.png', name='Join %s' % meeting.name,
                                                         description='Join https://meet.google.com/%s' % meeting.id,
                                                         on_enter=OpenUrlAction('https://meet.google.com/%s' % meeting.id)))

            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='Join meeting',
                                             description='Join https://meet.google.com/%s' % meet_id,
                                             on_enter=OpenUrlAction('https://meet.google.com/%s' % meet_id)))

        return RenderResultListAction(items)


if __name__ == '__main__':
    MeetExtension().run()
