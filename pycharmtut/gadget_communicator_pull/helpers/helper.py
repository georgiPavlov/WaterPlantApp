from django.forms import models


class BitChoices(object):
    def __init__(self, choices):
        self._choices = []
        self._lookup = {}
        for index, (key, val) in enumerate(choices):
            index = 2 ** index
            self._choices.append((index, val))
            self._lookup[key] = index

    def __iter__(self):
        return iter(self._choices)

    def __len__(self):
        return len(self._choices)

    def __getattr__(self, attr):
        try:
            return self._lookup[attr]
        except KeyError:
            raise AttributeError(attr)

    def get_selected_keys(self, selection):
        """ Return a list of keys for the given selection """
        return [k for k, b in self._lookup.iteritems() if b & selection]

    def get_selected_values(self, selection):
        """ Return a list of values for the given selection """
        return [v for b, v in self._choices if b & selection]


WEEKDAYS = BitChoices((('mon', 'Monday'), ('tue', 'Tuesday'), ('wed', 'Wednesday'),
                       ('thu', 'Thursday'), ('fri', 'Friday'), ('sat', 'Saturday'),
                       ('sun', 'Sunday')
                       ))
DATE_INPUT_FORMATS = ["%I:%M %p"]

WEEKDAYS_NUMERIC = dict({'Monday': 1, 'Tuesday': 2, 'Wednesday': 4, 'Thursday': 8, 'Friday': 16, 'Saturday': 32, 'Sunday': 64})

print(list(WEEKDAYS))
print(WEEKDAYS.fri)
# print(WEEKDAYS.get_selected_keys('mon'))
# print(WEEKDAYS.get_selected_values('Friday'))
if 'dd' in WEEKDAYS_NUMERIC.keys():
    print("Key exists")
else:
    print("Key does not exist")

