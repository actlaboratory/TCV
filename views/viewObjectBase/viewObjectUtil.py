#viewObjectUtil for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>


def popArg(kArg, arg, default=None):
    if arg in kArg: return kArg.pop(arg)
    else: return default
