def static_var(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

class ObjectView(object):
    def __init__(self, d):
        self.__dict__ = d
