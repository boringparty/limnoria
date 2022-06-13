# this accepts @champ or @constructor with an optional year
# and also @gp with an optional race number for the current season


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

    def champ(self, irc, msg, args, year):
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
            string_segments.append(f"\x035{name}\x0F {points}")

        irc.reply(", ".join(string_segments))

    champ = wrap(champ, [optional("int")])

    def gp(self, irc, msg, args, race):
        """<year>
        Call standings by year
        F1 Standings
        """

        data = requests.get("https://ergast.com/api/f1/current/last/results.json")
        if race:
            data = requests.get(
                "https://ergast.com/api/f1/current/%s/results.json" % (race)
            )
        driver_result = json.loads(data.content)["MRData"]["RaceTable"]["Races"][0][
            "Results"
        ]
        string_segments = []

        for driver in driver_result:
            name = driver["Driver"]["code"]
            position = driver["positionText"]
            points = driver["points"]
            string_segments.append(f"{position} \x035{name}\x0F {points}")

        irc.reply(", ".join(string_segments))

    gp = wrap(gp, [optional("int")])

    def constructor(self, irc, msg, args, year):
        """<year>
        Call standings by year
        F1 Standings
        """

        data = requests.get(
            "https://ergast.com/api/f1/current/constructorStandings.json"
        )
        if year:
            data = requests.get(
                "https://ergast.com/api/f1/current/constructorStandings.json" % (year)
            )
        driver_result = json.loads(data.content)["MRData"]["StandingsTable"][
            "StandingsLists"
        ][0]["ConstructorStandings"]
        string_segments = []

        for driver in driver_result:
            name = driver["Constructor"]["name"]
            position = driver["positionText"]
            points = driver["points"]
            string_segments.append(f"{position} \x035{name}\x0F {points}")

        irc.reply(", ".join(string_segments))

    constructor = wrap(constructor, [optional("int")])


Class = F1
