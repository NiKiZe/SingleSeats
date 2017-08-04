#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import re
import socket
import sys
from time import sleep, gmtime, strftime
from . import constants

class Handler:

    __events = {}
    __ignore = [
        constants.PLAYER_TAKES_FRONT_SHIELD_DAMAGE,
        constants.PLAYER_TAKES_SHIELD_DAMAGE,
        constants.SOMETHING_HITS_PLAYER,
        constants.INCOMING_COMMUNICATION_ALERT,
        constants.INCOMING_COMMUNICATION_ENEMY,
        constants.INCOMING_COMMUNICATION_STATION,
    ]
    re_front = re.compile("^%s[0-9]+$" % constants.FRONT_SHIELD_)

    @staticmethod
    def dump_events():
        print('enums')
        for k in sorted(Handler.__events):
            print('    %s = auto()' % k)

        print('current event states')
        for k, v in sorted(Handler.__events.items()):
            print('# %r' % v)

    @staticmethod
    def get_range(prefix):
        foundrange = 0
        # TODO this should probably have some smart mapping
        for i in range(20, 100 + 1, 20):
            event = Handler.__events.get('%s%i' % (prefix, i), None)
            if event is None:
                continue

            if event.state:
                foundrange = i
            else:
                break
        return foundrange

    @staticmethod
    def get_or_new_event(name):
        event = Handler.__events.get(name, None)
        if event is None:
            event = EventState(name)
            Handler.__events[name] = event
        return event

    @staticmethod
    def get_event_state(name, default_state = False):
        event = Handler.__events.get(name, None)
        if event is None or event.state is None:
            return default_state
        return event.state

    def __init__(self):
        self.frontShieldMinimum = 0
        self.frontShieldCurrent = 100

    def manage_events(self, name, state):
        if state != None:
            event = Handler.get_or_new_event(name)
            # dont handle already existing state
            if event.state == state:
                return
            event.count += 1
            event.state = state

            if state and name == constants.PLAYER_TAKES_FRONT_SHIELD_DAMAGE:
                # we don't know how much damage we took, but this is just an avg.
                self.frontShieldCurrent -= 1
                if self.frontShieldCurrent < self.frontShieldMinimum:
                    self.frontShieldCurrent = self.frontShieldMinimum
                else:
                    # intentionally not perfectly calculated
                    self.raise_incoming_event('Shield: %i %s' % \
                        (self.frontShieldCurrent, name), None)
            elif Handler.re_front.match(name): # front shield with number
                self.frontShieldMinimum = Handler.get_range(constants.FRONT_SHIELD_)
                level = int(name[len(constants.FRONT_SHIELD_):])
                if state:
                    # ensure shield is atleast at this level
                    if self.frontShieldCurrent < self.frontShieldMinimum:
                        self.frontShieldCurrent = self.frontShieldMinimum
                else:
                    # ensure shield is below this level
                    if level <= self.frontShieldCurrent:
                        self.frontShieldCurrent = level - 1
                self.raise_incoming_event('Shield: %i %s' % \
                    (self.frontShieldCurrent, name), None)
            
            docked = Handler.get_event_state(constants.FIGHTER_BAY_EXISTS, True)
            # don't spam anything if docked
            #if docked:
                #return
            if name in constants.SILENCED_EVENTS:
                return

        self.raise_incoming_event(name, state)

    def raise_incoming_event(self, name, state):
        # TODO fix real events
        print("%s: %s\t%s" % (strftime('%Y-%m-%d %H:%M:%S', gmtime()), name, state))


class HandlerStream(Handler):

    def handle_line(self, line):
        # todo move this to subclass
        parts = list(filter(None, line.split(' ')))
        # part 0 is time
        name = parts[1]
        assert parts[2] == "="
        state = int(parts[3]) == 1
        self.manage_events(name, state)


class HandlerTcp(HandlerStream):

    def __init__(self, server = '127.0.0.1', port = 23000):
        super(HandlerTcp, self).__init__()
        self.dorun = True
        self.server = server
        self.port = port
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    def connect(self):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.connect_inner)

    def kill(self):
        self.dorun = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print('Kill Exception:')
            print(e) #sys.exc_info()[0])
        finally:
            self.sock.close()

    def connect_inner(self):
        self.dorun = True
        self.raise_incoming_event( \
            "Start connection to %s:%i and listening for Artemis events\n" % \
            (self.server, self.port) + \
            "we expect ArtemisBridgeTools to have that log port open", None)
        # TODO handle exceptions and keep retrying in background loop
        while self.dorun:
            needconnect = True
            try:
                if needconnect:
                    print('Connecting ...')
                    self.sock.connect((self.server, self.port))
                    print('Connected')
                    needconnect = False
                self.run()
            except Exception as e:
                needconnect = True
                print('Connect inner Exception:')
                print(e)
                if isinstance(self.sock, socket.socket):
                    self.sock.close()
                sleep(3)

    def run(self):
        for line in self.sock.makefile():
            self.handle_line(line)


class EventState:

    def __init__(self, name):
        self.__name = name
        self.state = False
        self.count = 0

    @property
    def name(self):
        return self.__name

    def __repr__(self):
        return '%s\t%i\t%s' % \
            (self.name, self.count, self.state)
