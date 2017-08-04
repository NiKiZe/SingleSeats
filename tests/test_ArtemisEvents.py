#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ArtemisEvents import constants
import ArtemisEvents

def setupEngine(engine = ArtemisEvents.Handler()):
    def testline(l):
        pass
    engine.testline = testline

    # bay must be false to get events
    engine.manage_events(constants.FIGHTER_BAY_EXISTS, False)

    # reset shields
    engine.manage_events(constants.FRONT_SHIELD_20, True)
    engine.manage_events(constants.FRONT_SHIELD_40, True)
    engine.manage_events(constants.FRONT_SHIELD_60, True)
    engine.manage_events(constants.FRONT_SHIELD_80, True)
    engine.manage_events(constants.FRONT_SHIELD_100, True)

    def front_hit():
        engine.manage_events(constants.PLAYER_TAKES_FRONT_SHIELD_DAMAGE, True)
        engine.manage_events(constants.PLAYER_TAKES_FRONT_SHIELD_DAMAGE, False)
    engine.front_hit = front_hit

    return engine

def test_dump_events():
    engine = setupEngine()
    ArtemisEvents.Handler.dump_events()

def test_shield_down():
    engine = setupEngine()
    assert engine.frontShieldMinimum == 100
    assert engine.frontShieldCurrent == 100

    engine.manage_events(constants.FRONT_SHIELD_100, False)
    # since 100 goes of line that must mean that we now are at 99 or less
    # but 80 is still on so we can never go below that.
    assert engine.frontShieldMinimum == 80
    assert engine.frontShieldCurrent == 99

    engine.front_hit()
    assert engine.frontShieldMinimum == 80
    # hit lowers with 1
    assert engine.frontShieldCurrent == 98
    for i in range(17):
        engine.front_hit()
    assert engine.frontShieldCurrent == 81
    engine.front_hit()
    assert engine.frontShieldCurrent == 80

    engine.manage_events(constants.FRONT_SHIELD_80, False)
    assert engine.frontShieldMinimum == 60
    assert engine.frontShieldCurrent == 79

def test_shield_up():
    engine = setupEngine()
    engine.manage_events(constants.FRONT_SHIELD_100, False)
    engine.manage_events(constants.FRONT_SHIELD_80, False)
    assert engine.frontShieldMinimum == 60
    assert engine.frontShieldCurrent == 79

    # test value on restore
    engine.manage_events(constants.FRONT_SHIELD_80, True)
    assert engine.frontShieldMinimum == 80
    assert engine.frontShieldCurrent == 80

    ArtemisEvents.Handler.dump_events()

def test_lineparsing():
    engine = setupEngine(ArtemisEvents.HandlerStream())
    engine.handle_line("112312.123123   %s      =    0" % constants.FRONT_SHIELD_100)
    assert engine.frontShieldMinimum == 80
    assert engine.frontShieldCurrent == 99

    engine.handle_line("112313.123123   %s      =    1" % constants.FRONT_SHIELD_100)
    assert engine.frontShieldMinimum == 100
    assert engine.frontShieldCurrent == 100

def not_test_streamtcp():
    engine = setupEngine(ArtemisEvents.HandlerTcp())
    engine.connect()
    engine.kill()
    ArtemisEvents.Handler.dump_events()