__author__ = 'Eshin Kunishima'
__license__ = 'MIT License'

import time
import calendar


class Epoch():
    def __init__(self, epoch=None):
        if epoch:
            self.__epoch = int(epoch)
        else:
            self.__epoch = calendar.timegm(time.gmtime())

    def __int__(self):
        return self.__epoch

    def __str__(self):
        return time.strftime('%c', time.localtime(self.__epoch))