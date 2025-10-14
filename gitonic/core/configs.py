
from const import F_TRACKED, F_COMMIT, F_FORMATTER, F_CONTEXT
from conf import Config

baseconf = Config()
trackedconf = Config(F_TRACKED)
commitconf = Config(F_COMMIT)

formatterconf = Config(F_FORMATTER)
contextconf = Config(F_CONTEXT)


def loadall_configs():
    baseconf.load()
    trackedconf.load()
    commitconf.load()
    formatterconf.load()
    contextconf.load()


def saveall_configs():
    baseconf.save()
    trackedconf.save()
    commitconf.save()
    formatterconf.save()
    contextconf.save()
