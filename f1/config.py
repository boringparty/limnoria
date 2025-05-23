import supybot.conf as conf
import supybot.registry as registry

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization("F1")
except:

    _ = lambda x: x


def configure(advanced):

    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin("F1", True)


Advice = conf.registerPlugin("F1")
