#author: johnxguo
#date: 2018-11-4

import os
import time

class SpeedHelper:
    def __init__(self, markSize, sizeAll = 0):
        self.markSize = markSize
        self.sizeAll = sizeAll
        self.sizeDone = 0
        self.marks = [{'time':time.time(), 'size': 0}]

    def setSizeAll(self, sizeAll):
        self.sizeAll = sizeAll

    def mark(self, size_addition):
        self.sizeDone = self.sizeDone + size_addition
        self.marks.append({'time':time.time(), 'size':self.sizeDone})
        if len(self.marks) > self.markSize:
            self.marks.pop(0)

    def size_done(self):
        return self.sizeDone
    
    def size_all(self):
        return self.sizeAll

    def speed(self):
        sizediff = self.marks[-1]['size'] - self.marks[0]['size']
        timediff = self.marks[-1]['time'] - self.marks[0]['time']
        if timediff == 0:
            return 0
        return sizediff / timediff
