import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import requests
import json
import dateutil.parser
from datetime import datetime, timedelta
from supybot.commands import wrap, optional
import pycountry


try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization("F1")
except ImportError:
    _ = lambda x: x


class F1(callbacks.Plugin):
    """Uses API to retrieve information"""
    threaded = True

    def next(self, irc, msg, args, tz_offset):
        """[tz offset]
        Shows next race and session times with countdown and upcoming sessions excluding the countdown session.
        """
        try:
            offset = int(tz_offset)
        except:
            offset = 0

        data = requests.get("https://api.jolpi.ca/ergast/f1/current/next.json")
        race_data = json.loads(data.content)["MRData"]["RaceTable"]["Races"][0]

        def local_dt(date_str, time_str):
            dt = dateutil.parser.parse(date_str + " " + time_str.replace("Z", ""))
            return dt + timedelta(hours=offset)

        def format_dt(dt):
            return dt.strftime("%b %d @ %H:%M")

        now = datetime.utcnow() + timedelta(hours=offset)

        sessions = [
            ("P1", race_data["FirstPractice"]["date"], race_data["FirstPractice"]["time"]),
            ("P2", race_data["SecondPractice"]["date"], race_data["SecondPractice"]["time"]),
        ]

        try:
            sessions.append(("P3", race_data["ThirdPractice"]["date"], race_data["ThirdPractice"]["time"]))
        except:
            sessions.append(("S", race_data["Sprint"]["date"], race_data["Sprint"]["time"]))

        sessions += [
            ("Q", race_data["Qualifying"]["date"], race_data["Qualifying"]["time"]),
            ("GP", race_data["date"], race_data["time"]),
        ]

        next_session = None
        for label, date_str, time_str in sessions:
            session_time = local_dt(date_str, time_str)
            if session_time > now:
                next_session = (label, session_time)
                break

        countdown = ""
        if next_session:
            delta = next_session[1] - now
            days = delta.days
            hours, rem = divmod(delta.seconds, 3600)
            minutes = rem // 60
            countdown = (
                f"Next: \x0304,15 {next_session[0]} \x0F "
                f"\x0304in {days}d {hours}h {minutes}m\x0F "
                f"(\x0301{format_dt(next_session[1])}\x0F), "
            )

        filtered_sessions = [
            (label, local_dt(date_str, time_str))
            for label, date_str, time_str in sessions
            if local_dt(date_str, time_str) > now and label != next_session[0]
        ]

        def label_str(tag, dt):
            return f"\x0301,15 {tag} \x0F {format_dt(dt)}"

        session_strs = [label_str(lbl, dt) for lbl, dt in filtered_sessions]

        circuit = race_data["Circuit"]["circuitName"]
        location = race_data["Circuit"]["Location"]["locality"]
        country = race_data["Circuit"]["Location"]["country"]

        reply = (
            f"\x02\x0301,15\u00A0{circuit}\u00A0\x0F (\x1D{location}, {country}\x1D) "
            f"\x034{countdown}\x0F" + ",  ".join(session_strs)
        )

        irc.reply(reply)

    next = wrap(next, [optional("something")])

    def champ(self, irc, msg, args, year):
        """<year>
        Call standings by year
        F1 Standings
        """
        url = f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json" if year in range(2005, 3000) else "https://api.jolpi.ca/ergast/f1/current/driverStandings.json"
        data = requests.get(url)
        standings = json.loads(data.content)["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]

        segments = [
            f"{d['positionText']}. {d['Driver']['code']} \x033[{d['points']}]\x0F"
            for d in standings if int(d['points']) > 0
        ]

        irc.reply(", ".join(segments))

    champ = wrap(champ, [optional("int")])

    def gp(self, irc, msg, args, race):
        """<race>
        GP Results
        """

        if race in range(1, 22):
            fastest = requests.get(f"https://api.jolpi.ca/ergast/f1/current/{race}/fastest/1/results.json")
            results = requests.get(f"https://api.jolpi.ca/ergast/f1/current/{race}/results.json")
        else:
            fastest = requests.get("https://api.jolpi.ca/ergast/f1/current/last/fastest/1/results.json")
            results = requests.get("https://api.jolpi.ca/ergast/f1/current/last/results.json")

        fastest_result = json.loads(fastest.content)["MRData"]["RaceTable"]["Races"][0]["Results"]
        fast_name = fastest_result[0]["Driver"]["code"]
        fast_time = fastest_result[0]["FastestLap"]["Time"]["time"]

        race_info = json.loads(results.content)["MRData"]["RaceTable"]["Races"][0]
        race_name = race_info["raceName"].replace("Grand Prix", "").strip()

        positions = []
        for r in race_info["Results"]:
            pos = r["positionText"]
            if pos == "R":
                pos = "\x035R\x0F"
            code = r["Driver"]["code"]
            positions.append(f"{pos}. {code}")

        prefix = "\x0301,15 "
        suffix = f"  \x0301,03 {fast_name} {fast_time} \x0F"

        result_str = ", ".join(positions).replace(" \x033[0]\x0F", "")
        irc.reply(f"{prefix}{race_name} \x0F{result_str}{suffix}")

    gp = wrap(gp, [optional("int")])



    def constructor(self, irc, msg, args, year):
        """<year>
        Call standings by year
        F1 Standings
        """
        url = f"https://api.jolpi.ca/ergast/f1/{year}/constructorStandings.json" if year in range(1958, 3000) else "https://api.jolpi.ca/ergast/f1/current/constructorStandings.json"
        data = requests.get(url)
        standings = json.loads(data.content)["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]

        segments = [
            f"{d['positionText']}. {d['Constructor']['name']} \x033[{d['points']}]\x0F"
            for d in standings if int(d['points']) > 0
        ]

        irc.reply(", ".join(segments))

    constructor = wrap(constructor, [optional("int")])


    def calendar(self, irc, msg, args, year):
        """<year>
        F1 race calendar by year
        """
        import pycountry
        from datetime import datetime

        special_codes = {
            "Las Vegas": "LV",
            "Miami": "MIA",
            "São Paulo": "SP",
            "Mexico City": "MEX",
            "Abu Dhabi": "AD",
            "Monte-Carlo": "MON",
            "Sakhir": "BAH",
            "Austin": "USA",
            "Imola": "EMI",
            "Budapest": "HUN",
            "Zandvoort": "NED",
        }

        url = f"https://api.jolpi.ca/ergast/f1/{year}.json" if year in range(1950, 3000) else "https://api.jolpi.ca/ergast/f1/current.json"
        data = requests.get(url)
        races = json.loads(data.content)["MRData"]["RaceTable"]["Races"]

        segments = []
        today = datetime.utcnow()

        next_highlighted = False
        for r in races:
            race_date = dateutil.parser.parse(r["date"])
            date_str = race_date.strftime("%m/%d")
            loc = r["Circuit"]["Location"]
            locality = loc["locality"]
            country = loc["country"]

            code = special_codes.get(locality)
            if not code:
                try:
                    code = pycountry.countries.lookup(country).alpha_3
                except LookupError:
                    code = country[:3].upper()

            text = f"\x02{code}\x0F {date_str}"

            if not next_highlighted and race_date > today:
                text = f"\x034,15{text}\x03"  # red text
                next_highlighted = True

            segments.append(text)

        irc.reply(", ".join(segments))

    calendar = wrap(calendar, [optional("int")])



Class = F1
