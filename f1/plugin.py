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
import dateutil.parser

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("F1")
except ImportError:
    _ = lambda x: x


class F1(callbacks.Plugin):
    """Uses API to retrieve information"""

    threaded = True

    def race(self, irc, msg, args, number):
        """<number>
        Call standings by year
        F1 Standings
        """

        data = requests.get("https://ergast.com/api/f1/current/next.json")
        if number:
            data = requests.get("https://ergast.com/api/f1/current/%s.json" % (number))

        race_times = json.loads(data.content)["MRData"]["RaceTable"]["Races"]
        string_segments = []

        for driver in race_times:

            P1 = "\x035P1\x0F " + dateutil.parser.parse(
                driver["FirstPractice"]["date"] + " " + driver["FirstPractice"]["time"]
            ).strftime("%b %d @ %H:%M")
            P2 = "\x035P2\x0F " + dateutil.parser.parse(
                driver["SecondPractice"]["date"]
                + " "
                + driver["SecondPractice"]["time"]
            ).strftime("%b %d @ %H:%M")
            try:
                P3 = "\x035P3\x0F " + dateutil.parser.parse(
                    driver["ThirdPractice"]["date"]
                    + " "
                    + driver["ThirdPractice"]["time"]
                ).strftime("%b %d @ %H:%M")
            except Exception:
                P3 = "\x035S\x0F " + dateutil.parser.parse(
                    driver["Sprint"]["date"] + " " + driver["Sprint"]["time"]
                ).strftime("%b %d @ %H:%M")

            circuit = driver["Circuit"]["circuitName"]
            location = driver["Circuit"]["Location"]["locality"]
            country = driver["Circuit"]["Location"]["country"]
            date = driver["date"] + " " + driver["time"].replace("Z", "")
            dt = dateutil.parser.parse(date).strftime("%b %d @ %H:%M")

            string_segments.append(
                f"\x02\x035{circuit}\x0F ({location}, {country}) {dt} {P1}, {P2}, {P3}"
            )

        irc.reply(", ".join(string_segments))

    race = wrap(race, [optional("int")])

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

    def calendar(self, irc, msg, args, year):
        """<year>
        Call standings by year
        F1 Standings
        """

        data = requests.get("https://ergast.com/api/f1/current.json")
        if year:
            data = requests.get("https://ergast.com/api/f1/%s.json" % (year))
        driver_standings = json.loads(data.content)["MRData"]["RaceTable"]["Races"]
        string_segments = []

        for driver in driver_standings:
            name = driver["raceName"].replace("Grand Prix", "")
            position = driver["round"]
            date = dateutil.parser.parse(driver["date"]).strftime("%m/%d")
            string_segments.append(f"\x035 {name}\x0F{date}")

        irc.reply(",".join(string_segments))

    calendar = wrap(calendar, [optional("int")])


Class = F1
