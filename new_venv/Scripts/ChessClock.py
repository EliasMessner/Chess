import time


class ChessClock:

    def __init__(self, initTime, whiteToMove=True):
        """
        :param initTime: a pair of the two time values in seconds, for example (7*60, 7*60) for initial time of 7<
        minutes for both players
        :type initTime: (int, int)
        """
        self.running = False
        self._lastTimeUpdated = time.time()
        self.currentTime = initTime
        self.whiteToMove = whiteToMove

    def start(self):
        self._lastTimeUpdated = time.time()
        self.running = True

    def stop(self):
        self.running = False

    def startStop(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def getTime(self):
        self._update()
        return self.currentTime

    def switchPlayer(self):
        self.whiteToMove = not self.whiteToMove

    def reset(self, value):
        self.currentTime = value
        self.running = False

    def _update(self):
        if self.running and 0 not in self.currentTime:
            seconds_diff = time.time() - self._lastTimeUpdated
            if self.whiteToMove:
                self.currentTime = (max(self.currentTime[0] - seconds_diff, 0), self.currentTime[1])
            else:
                self.currentTime = (self.currentTime[0], max(self.currentTime[1] - seconds_diff, 0))
            self._lastTimeUpdated = time.time()
