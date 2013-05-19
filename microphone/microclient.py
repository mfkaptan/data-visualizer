import sys, json, alsaaudio, audioop

from twisted.internet import reactor
from autobahn.websocket import WebSocketClientFactory, \
                                         WebSocketClientProtocol, \
                                         connectWS

class Microphone():
    def __init__(self):
        self.inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK)

        # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
        self.inp.setchannels(1)
        self.inp.setrate(8000)
        self.inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.inp.setperiodsize(160)

    def get_level(self):
        # Read data from device
        l, data = self.inp.read()
        if l:
            # Return the maximum of the absolute value of
            # all samples in a fragment.
            level = audioop.max(data, 2)
            # 'Level' should fit the screen when we draw it.
            # Max value of the 'level' is 32767.
            # In .html file, screen height is 500.
            # So let's divide 'level' by for example 65.
            # So that it can fit to the screen
            return str(level // 65)
        else:
            return str(0)

class BroadcastClientProtocol(WebSocketClientProtocol):
    """
    Simple client that connects to a WebSocket server, send the Microphone's
    data every 0.015 seconds and print everything it receives.
    """
    def __init__(self):
        self.mic = Microphone()

    def sendLevel(self):
        self.sendMessage(self.mic.get_level())
        # Next data in 15 Miliseconds
        reactor.callLater(0.015, self.sendLevel)

    def onOpen(self):
        self.sendLevel()

    def onMessage(self, msg, binary):
        pass
        # Debug
        # print "Got message: " + msg

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Need the WebSocket server address, i.e. ws://localhost:9000"
        sys.exit(1)

    factory = WebSocketClientFactory(sys.argv[1])
    factory.protocol = BroadcastClientProtocol
    connectWS(factory)

    reactor.run()
