import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import requests
import os
import collections
import json

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("F1")
except ImportError:
    _ = lambda x: x


class F1(callbacks.Plugin):
    """Uses API to retrieve information"""

    threaded = True

    def f1(self, irc, msg, args, year):
        """<year>
        Call standings by year
        F1 Standings
        """

        data = requests.get("https://ergast.com/api/f1/current/driverStandings.json")
        if year:
            data = requests.get(
                "https://ergast.com/api/f1/%s/driverStandings.json" % (year)
            )
        driver_standings = json.loads(data.content)["MRData"]["StandingsTable"][
            "StandingsLists"
        ][0]["DriverStandings"]
        string_segments = []

        for driver in driver_standings:
            name = driver["Driver"]["code"]
            position = driver["positionText"]
            points = driver["points"]
            string_segments.append(f"\x031,82 {name} {points} \x0F")

        irc.reply(" ".join(string_segments))

    f1 = wrap(f1, [optional("int")])


Class = F1
