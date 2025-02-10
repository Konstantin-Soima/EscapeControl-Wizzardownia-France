import socket
import struct
import subprocess
import telnetlib
import time
import psutil # type: ignore
import fcntl
import os
import builtins
from threading import Timer


class EscapeControlAPI:
    """ EscapeControl API for python clients """

    # commands (first bytes)
    CMD_PING_REQ = 0x10
    CMD_PING_RESP = 0x11
    CMD_POWERON = 0x12
    # !!!3,4 occupied by params
    CMD_HALT = 0x0E

    CMD_EXT_MISO = 0xe0
    CMD_EXT_MOSI = 0xe1

    CMD_TM1637_INIT = 0xA5
    CMD_TM1637_DISPLAYDEC = 0xA6
    CMD_TM1637_DISPLAY_BRIGHTNESS = 0xA7
    CMD_TM1637_DISPLAYHEX = 0xA8

    CMD_LIQUID_CRYSTAL_INIT = 0xAA
    CMD_LIQUID_CRYSTAL_BACKLIGHT = 0xAB
    CMD_LIQUID_CRYSTAL_CURSOR = 0xAC
    CMD_LIQUID_CRYSTAL_PRINT = 0xAD
    CMD_LIQUID_CRYSTAL_BLINK = 0xAE

    CMD_KEYPAD_REQUEST = 0xf0
    CMD_KEYPAD_RESPONSE = 0xf1
    CMD_KEYPAD_SET = 0xf2

    CMD_GPIO_PINMODE = 0xc0
    CMD_GPIO_DIGITALWRITE = 0xc1
    CMD_GPIO_DIGITALREAD = 0xC2
    CMD_GPIO_ANALOGREAD = 0xC3
    CMD_GPIO_DIGITALREAD_RESPONSE = 0xC4
    CMD_GPIO_SEND_DIGITAL_CHANGE = 0xCF
    CMD_GPIO_SEND_DIGITAL_CHANGE_INITIAL = 0xCE
    CMD_GPIO_ANALOGWRITE = 0xC7
    CMD_GPIO_UPDATE_LIST = 0xC8
    CMD_GPIO_REFRESH = 0xC9
    CMD_GPIO_ANALOGREAD_RESPONSE = 0xC5
    CMD_GPIO_TONE = 0xCA
    CMD_GPIO_NOTONE = 0xCB
    CMD_GPIO_DIGITALREADLIST = 0xCC
    CMD_GPIO_DIGITALREADLIST_RESPONSE = 0xCD

    CMD_MASTER_REBOOT = 0x00
    CMD_MASTER_UNLOCK = 0x01
    CMD_MASTER_BOOTLOADER = 0x02
    CMD_MASTER_STARTSCRIPT = 0x03
    CMD_MASTER_STOPSCRIPT = 0x04
    CMD_MASTER_AVR_FIRMWARE = 0x05
    CMD_MASTER_SCRIPTSTATUS = 0x06
    CMD_MASTER_RELOAD = 0x07
    CMD_MASTER_LOG = 0x08
    CMD_MASTER_AVRON = 0x09
    CMD_MASTER_AVROFF = 0x0A
    CMD_MASTER_LASTRESP = 0x0B
    CMD_MASTER_LOCALIP = 0x0C
    CMD_MASTER_OFFLINE = 0x0D
    CMD_MASTER_STATISTICS = 0x0F
    CMD_MASTER_SCRIPTSTARTED = 0xFE
    CMD_MASTER_SET_PARAMETER = 0x13
    CMD_MASTER_GET_PARAMETER = 0x14

    CMD_VIDEO_PLAYFILE = 0xD0
    CMD_VIDEO_PLAYCURRENT = 0xD1
    CMD_VIDEO_PAUSE = 0xD2
    CMD_VIDEO_STOP = 0xD3
    CMD_VIDEO_SEEK = 0xD4
    CMD_VIDEO_GET_POSITION = 0xD5
    CMD_VIDEO_GET_LENGTH = 0xD6
    ANS_VIDEO_POSITION = 0xD7
    ANS_VIDEO_LENGTH = 0xD8
    CMD_VIDEO_PLAYURL = 0xD9
    CMD_VIDEO_VOLUME = 0xA0

    CMD_DFPLAYER_PLAYFOLDER = 0x20
    CMD_DFPLAYER_START = 0x21
    CMD_DFPLAYER_PAUSE = 0x22
    CMD_DFPLAYER_STOP = 0x23
    CMD_DFPLAYER_VOLUME = 0x24
    CMD_DFPLAYER_BEGIN = 0x25
    CMD_DFPLAYER_END = 0x26

    CMD_RFID_DO = 0x50
    ANS_RFID_DO = 0x51

    CMD_CAPSENSE_DO = 0xB0
    ANS_CAPSENSE_DO = 0xB1

    CMD_WS2812_INIT = 0x30
    CMD_WS2812_SET = 0x31
    CMD_WS2812_SYNC = 0x32

    TCP_IP = '127.0.0.1'
    TCP_PORT = 4459
    BUFFER_SIZE = 500
    s = 0
    quest_tcp = struct.Struct('15s B I 480s')
    bytes_4 = struct.Struct('BBBB')
    bytes_3 = struct.Struct('BBB')
    bytes_2 = struct.Struct('BB')

    def __del__(self):
        """ Close the socket and destroy object """
        print("closing socket...")
        try:
            self.s.shutdown(1)
            self.s.close()
        except:
            print("can't close")

    def __init__(self):
        """ Constructor """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.TCP_IP, self.TCP_PORT))
        except:
            print("Can't connect!")

    def send(self, msg):
        """ Send raw message """
        slen = 0
        while slen <= 0:
            try:
                slen = self.s.send(msg)
            except:
                slen = 0
            if slen <= 0:
                time.sleep(0.5)
                print("reconnecting...")
                self.__init__()
            else:
                time.sleep(0.002)
                return slen

    def recv(self, bufsize):
        """ Receive raw message """
        dlen = 0
        while dlen <= 0:
            try:
                data = self.s.recv(bufsize)
            except:
                data = ""
            dlen = len(data)
            if dlen <= 0:
                time.sleep(0.5)
                print("reconnecting...")
                self.__init__()
            else:
                return data

    def get_msg(self, start_time=None):
        """ Get and parse message """
        sym = self.recv(self.BUFFER_SIZE)
        sym += bytes('0' * (EscapeControlAPI.BUFFER_SIZE - len(sym)), 'ascii')
        res = list(self.quest_tcp.unpack(sym))
        res[3] = res[3][:res[1]]
        res[0] = res[0][:res[0].find(b'\x00')]
        # print("> " + str(res))
        if start_time == None:
            return res
        else:
            if int(start_time) <= int(res[2]):
                return res
            else:
                return None

    def send_msg(self, msg):
        """ Parse and send message """
        msg[2] = int(time.time())
        self.send(self.quest_tcp.pack(*msg))
        # print("< " + str(msg))

    def msg_is_offline(self, device, msg):
        """ Does the message say that the device is offline? """
        if msg[0] == bytes(str(device), 'ascii'):
            if msg[1] == 1:
                if msg[3][0] == self.CMD_MASTER_OFFLINE:
                    print("ERROR: device is offline!")
                    time.sleep(0.01)
                    return True
        return False

    def getCurrentID(self):
        """ Return ID of the currently running scenario or 0 if not running in a scenario """
        try:
            current_id = int(builtins.scenario_name.split('_')[1])
        except:
            current_id = 0
        return current_id

    # class: GPIO
    def GPIOWait(self, device, pin, value):
        """ Wait for a specific value on pin """
        self.GPIOUpdateList(device, [pin])
        start_time = time.time()
        msg1 = self.bytes_3.pack(self.CMD_GPIO_DIGITALREAD, pin, 0)
        msg2 = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg2)
        res_time = 0
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                dr = list(self.bytes_3.unpack(msg[3][:3]))
                if dr[0] in [self.CMD_GPIO_SEND_DIGITAL_CHANGE, self.CMD_GPIO_SEND_DIGITAL_CHANGE_INITIAL,
                             self.CMD_GPIO_DIGITALREAD_RESPONSE]:
                    if dr[1] == pin and dr[2] == value:
                        if dr[0] == self.CMD_GPIO_SEND_DIGITAL_CHANGE:
                            res_time = struct.Struct('<I').unpack(msg[3][3:7])[0]
                        self.GPIOUpdateList(device, [])
                        return res_time

    # class: GPIO
    def GPIOWaitAny(self, device, pin):
        """ Wait for any value change on pin """
        start_time = time.time()
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                dr = list(self.bytes_3.unpack(msg[3][:3]))
                if dr[0] in [self.CMD_GPIO_SEND_DIGITAL_CHANGE, self.CMD_GPIO_SEND_DIGITAL_CHANGE_INITIAL]:
                    if dr[1] == pin:
                        return dr[2]

    # class: GPIO
    def GPIOMode(self, device, pin, mode):
        """ Set the mode of the pin using Arduino's pinMode() """
        msg1 = self.bytes_3.pack(self.CMD_GPIO_PINMODE, pin, mode)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: GPIO
    def GPIOSet(self, device, pin, value):
        """ Set digital value on a pin """
        self.GPIOMode(device, pin, 1)
        if isinstance(value, (float, int)):
            msg1 = self.bytes_3.pack(self.CMD_GPIO_DIGITALWRITE, pin, value)
            msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
            self.send_msg(msg)

    # class: GPIO
    def GPIOUpdateList(self, device, pins):
        """ Update list of pins which need to be monitored """
        msg1 = struct.Struct('BB' + str(len(pins)) + 'B').pack(self.CMD_GPIO_UPDATE_LIST, len(pins), *pins)
        msg = [bytes(str(device), 'ascii'), 110, 0, msg1]
        self.send_msg(msg)

    # class: GPIO
    def GPIORefresh(self, device):
        """ Update pin monitor manuallt """
        msg1 = struct.Struct('B').pack(self.CMD_GPIO_REFRESH)
        msg = [bytes(str(device), 'ascii'), 1, 0, msg1]
        self.send_msg(msg)

    # class: GPIO
    def GPIOSetAnalog(self, device, pin, value):
        """ Set analog value on a pin """
        msg1 = self.bytes_3.pack(self.CMD_GPIO_ANALOGWRITE, pin, value)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: GPIO
    def GPIOReadNoPullup(self, device, pin):
        """ Read digital value on a pin, without pullup """
        start_time = time.time()
        msg1 = self.bytes_3.pack(self.CMD_GPIO_DIGITALREAD, pin, 0)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)
        resender = ResendMessageTimer(self, msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                resender.stop()
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                dr = list(self.bytes_3.unpack(msg[3][:3]))
                if dr[0] in [self.CMD_GPIO_DIGITALREAD_RESPONSE]:
                    if dr[1] == pin:
                        resender.stop()
                        return dr[2]

    # class: GPIO
    def GPIORead(self, device, pin):
        """ Read digital value on a pin, with pullup """
        self.GPIOMode(device, pin, 2)
        return self.GPIOReadNoPullup(device, pin)

    # class: GPIO
    def GPIOReadList(self, device, pins):
        """ Read digital values on pins atomically """
        start_time = time.time()
        struct_pins_req = struct.Struct('BB' + 'B' * len(pins))
        struct_pins_resp = struct.Struct('BB' + 'B' * 2 * len(pins))
        msg1 = struct_pins_req.pack(self.CMD_GPIO_DIGITALREADLIST, len(pins), *pins)
        msg = [bytes(str(device), 'ascii'), 2 + len(pins), 0, msg1]
        self.send_msg(msg)
        resender = ResendMessageTimer(self, msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                resender.stop()
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                try:
                    dr = list(struct_pins_resp.unpack(msg[3][:2 + 2 * len(pins)]))
                    if dr[0] == self.CMD_GPIO_DIGITALREADLIST_RESPONSE:
                        if dr[1] == len(pins) and dr[2:2 + len(pins)] == pins:
                            resender.stop()
                            return dr[2 + len(pins):2 + 2 * len(pins)]
                except:
                    pass

    # class: GPIO
    def GPIOReadAnalog(self, device, pin):
        """ Get analog value on a pin """
        start_time = time.time()
        msg1 = self.bytes_3.pack(self.CMD_GPIO_ANALOGREAD, pin, 0)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                dr = list(self.bytes_3.unpack(msg[3][:3]))
                if dr[0] in [self.CMD_GPIO_ANALOGREAD_RESPONSE]:
                    if dr[1] == pin:
                        return dr[2]

    # class: GPIO
    def GPIOTone(self, device, pin, frequency):
        """ Call Arduino's tone() function """
        msg1 = struct.Struct('BB').pack(self.CMD_GPIO_TONE, pin)
        msg2 = struct.Struct('<H').pack(frequency)
        msg3 = msg1 + msg2
        msg = [bytes(str(device), 'ascii'), 4, 0, msg3]
        self.send_msg(msg)

    # class: GPIO
    def GPIONoTone(self, device, pin):
        """ Call Arduino's noTone() function """
        msg1 = struct.Struct('BB').pack(self.CMD_GPIO_NOTONE, pin)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: Keypad
    def KeypadSet(self, device, keypad, row_pins, col_pins):
        """ Initialize keypad with row_pins and col_pins """
        S = 10
        row_pins = row_pins[:S]
        col_pins = col_pins[:S]
        row_n = len(row_pins)
        col_n = len(col_pins)
        row_pins = row_pins + [0] * (S - row_n)
        col_pins = col_pins + [0] * (S - col_n)
        msg1 = struct.Struct('BBBB' + '10B10B').pack(self.CMD_KEYPAD_SET, keypad, row_n, col_n, *(row_pins + col_pins))
        msg = [bytes(str(device), 'ascii'), 24, 0, msg1]
        self.send_msg(msg)

    # class: Keypad
    def KeypadGetActive(self, device, keypad):
        """ Get currently pressed keys on a keypad """
        msg1 = struct.Struct('BB').pack(self.CMD_KEYPAD_REQUEST, keypad)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        start_time = time.time()
        self.send_msg(msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 1 and msg[3][0] == self.CMD_KEYPAD_RESPONSE and \
                    msg[3][1] == keypad:
                l = msg[3][2]
                return list(msg[3][3:3 + l])

    # class: Ext
    def ExtMOSI(self, device, cmd):
        """ Send data to an external device """
        if len(cmd) > 300:
            cmd = cmd[:300]
        if type(cmd) == type('a'):
            cmd = bytes(cmd, 'ascii')
        msg1 = struct.Struct('B' + str(len(cmd)) + 's').pack(self.CMD_EXT_MOSI, cmd)
        msg = [bytes(str(device), 'ascii'), 1 + len(cmd), 0, msg1]
        self.send_msg(msg)

    # class: Ext
    def ExtMISO(self, device):
        """ Receive data from an external device """
        while True:
            msg = self.get_msg(None)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 1 and msg[3][0] == self.CMD_EXT_MISO:
                return str(msg[3][1:])

    # class: General
    def AVRFlashBootloader(self, device_id):
        """ Flash bootloader to a currently connected USB device """
        msg1 = self.bytes_2.pack(self.CMD_MASTER_BOOTLOADER, int(device_id))
        msg = [bytes("master", 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: General
    def DaemonReboot(self):
        """ Restart the daemon program """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_REBOOT)
        msg = [bytes("master", 'ascii'), 1, 0, bb]
        self.send_msg(msg)

    # class: General
    def LocksGetN(self):
        """ Maximal lock ID """
        return 0xff + 1

    # class: General
    def LocksWait(self, n):
        """ Wait until lock is unlocked """
        self.s.settimeout(None)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 2:
                dr = list(self.bytes_2.unpack(msg[3][:2]))
                if dr[0] in [self.CMD_MASTER_UNLOCK]:
                    if dr[1] == n:
                        self.s.settimeout(1)
                        return

    # class: General
    def LocksWaitMany(self, array):
        """ Wait untill all locks in array are unlocked, in any order """
        array = [int(x) for x in set(array)]
        if len(array) == 0:
            return
        self.s.settimeout(None)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 2:
                dr = list(self.bytes_2.unpack(msg[3][:2]))
                if dr[0] in [self.CMD_MASTER_UNLOCK]:
                    if dr[1] in array:
                        del array[array.index(dr[1])]
                        if len(array) == 0:
                            self.s.settimeout(1)
                            return

    # class: General
    def LocksUnlock(self, n):
        """ Unlock one lock """
        msg1 = self.bytes_3.pack(self.CMD_MASTER_UNLOCK, n, self.getCurrentID())
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: General
    def AVRCode(self, physical_device, hex_file):
        """ Copy the file in the RPI filesystem as Arduino firmware """
        t = bytearray(hex_file, 'ascii')
        t.append(0x00)
        msg1 = self.bytes_2.pack(self.CMD_MASTER_AVR_FIRMWARE, physical_device)
        msg1 += t
        msg = [bytes("master", 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: General
    def ScenarioStart(self, id, slot=-1):
        """ Start one scenario """
        current_id = self.getCurrentID()
        msg1 = self.bytes_4.pack(self.CMD_MASTER_STARTSCRIPT, id, current_id, get_slot_safe(slot))
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: General
    def ScenarioStop(self, id, slot=-1):
        """ Stop one scenario """
        msg1 = self.bytes_3.pack(self.CMD_MASTER_STOPSCRIPT, id, get_slot_safe(slot))
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: General
    def ScenarioStatus(self, id, slot=-1):
        """ Is scenario running? """
        msg1 = self.bytes_3.pack(self.CMD_MASTER_SCRIPTSTATUS, id, get_slot_safe(slot))
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 3:
                lst = list(self.bytes_3.unpack(msg[3][:3]))
                if lst[0] in [self.CMD_MASTER_SCRIPTSTATUS]:
                    if lst[1] == id:
                        return lst[2]

    # class: General
    def DaemonStatistics(self):
        """ Get statistics for the daemon: running/finished scenarios, number of online devices """
        msg1 = self.bytes_2.pack(self.CMD_MASTER_STATISTICS, 0)
        msg = [bytes("master", 'ascii'), 2, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 4:
                lst = list(self.bytes_4.unpack(msg[3][:4]))
                if lst[0] in [self.CMD_MASTER_STATISTICS]:
                    return lst[1], lst[2], lst[3]

    # class: General
    def ScenarioWasStarted(self, id, slot):
        """ Was scenario started? """
        msg1 = self.bytes_3.pack(self.CMD_MASTER_SCRIPTSTARTED, id, slot)
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 3:
                lst = list(self.bytes_3.unpack(msg[3][:3]))
                if lst[0] in [self.CMD_MASTER_SCRIPTSTARTED]:
                    if lst[1] == id:
                        return lst[2]

    # class: General
    def ScenarioStatusAndParent(self, id, slot):
        """ Get status of the scenario and scenario ID which started it """
        msg1 = self.bytes_3.pack(self.CMD_MASTER_SCRIPTSTATUS, id, slot)
        msg = [bytes("master", 'ascii'), 3, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 4:
                lst = list(self.bytes_4.unpack(msg[3][:4]))
                if lst[0] in [self.CMD_MASTER_SCRIPTSTATUS]:
                    if lst[1] == id:
                        return lst[2], lst[3]

    # class: General
    def Reload(self):
        """ Reconnect to devices and reload scenarios """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_RELOAD)
        msg = [bytes("master", 'ascii'), 1, 0, bb]
        self.send_msg(msg)

    # class: General
    def HaltMaster(self):
        """ Turn off main raspberry """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_HALT)
        msg = [bytes("master", 'ascii'), 1, 0, bb]
        self.send_msg(msg)

    # class: General
    def Halt(self, device):
        """ Halt one device """
        msg1 = self.bytes_3.pack(self.CMD_HALT, 0, 0)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: General
    def Log(self, logstr):
        """ Append a string to the log """
        try:
            name = builtins.scenario_name + ": "
        except:
            name = ""
        logstr = name + str(logstr)
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_LOG)
        bb += bytearray(logstr, 'ascii')
        length = len(bb)
        if length > 255:
            length = 255
            bb = bb[:255]
        msg = [bytes("master", 'ascii'), length, 0, bb]
        self.send_msg(msg)

    # class: General
    def SetParameter(self, paramName, paramValue):
        """ Set global parameter with main scenario lifescope """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_SET_PARAMETER)
        bb.append(get_slot_safe(-1))
        bb.append(paramValue)
        bb += bytearray(paramName, 'ascii')
        length = len(bb)
        msg = [bytes("master", 'ascii'), length, 0, bb]
        self.send_msg(msg)

    # class: General
    def GetParameter(self, paramName):
        """ Get game parameter value """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_GET_PARAMETER)
        bb.append(get_slot_safe(-1))
        bb += bytearray(paramName, 'ascii')
        length = len(bb)
        msg = [bytes("master", 'ascii'), length, 0, bb]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg is None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 4:
                lst = list(self.bytes_3.unpack(msg[3][:3]))
                if lst[0] in [self.CMD_MASTER_SET_PARAMETER]:
                    if lst[1] == get_slot_safe(-1) and msg[3][3:len(paramName) + 3].decode('ascii') == paramName:
                        return lst[2]

    # class: General
    def AVROn(self):
        """ Turn AVR devices ON """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_AVRON)
        msg = [bytes("master", 'ascii'), 1, 0, bb]
        self.send_msg(msg)

    # class: General
    def AVROff(self):
        """ Turn AVR devices OFF """
        bb = bytearray("", 'ascii')
        bb.append(self.CMD_MASTER_AVROFF)
        msg = [bytes("master", 'ascii'), 1, 0, bb]
        self.send_msg(msg)

    # class: General
    def AVRReboot(self, delay=5):
        """ Reboot AVR devices """
        self.AVROff()
        time.sleep(delay)
        self.AVROn()

    # class: General
    def LastSeen(self, id):
        """ When did the device respond the last time? """
        start_time = time.time()
        msg1 = self.bytes_2.pack(self.CMD_MASTER_LASTRESP, id)
        msg = [bytes("master", 'ascii'), 2, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and msg[1] >= 10:
                lst = list(struct.unpack("Q", msg[3][2:10]))
                if int(msg[3][0:1][0]) == self.CMD_MASTER_LASTRESP:
                    if int(msg[3][1:2][0]) == id:
                        return lst[0]

    # class: General
    def GetLocalIP(self):
        """ Get Local IP of the main RPI """
        msg1 = bytearray(0)
        msg1.append(self.CMD_MASTER_LOCALIP)
        msg = [bytes("master", 'ascii'), 1, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if msg[0] == bytes("master", 'ascii') and int(msg[3][0:1][0]) == self.CMD_MASTER_LOCALIP:
                return str(msg[3][1:msg[1] - 1])

    # class: General
    def ShowLog(self):
        """ Print log messages """
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            else:
                print(msg)

    # class: TM1637
    def TM1637Begin(self, device, tm_id, clk_pin, dio_pin):
        """ Connect to TM1637 chip """
        msg1 = struct.Struct('BBBB').pack(self.CMD_TM1637_INIT, tm_id, clk_pin, dio_pin)
        msg = [bytes(str(device), 'ascii'), 4, 0, msg1]
        self.send_msg(msg)

    # class: TM1637
    def TM1637DisplayDec(self, device, tm_id, lst):
        """ Display a number as a list of 4 digits """
        assert len(lst) == 4, "Wrong number of digits (should be 4)"
        lst = list(map(int, lst))
        msg1 = struct.Struct('BBBBBB').pack(self.CMD_TM1637_DISPLAYDEC, tm_id, lst[0], lst[1], lst[2], lst[3])
        msg = [bytes(str(device), 'ascii'), 6, 0, msg1]
        self.send_msg(msg)

    # class: TM1637
    def TM1637DisplayHex(self, device, tm_id, lst):
        """ Display segments on display based on hex """
        assert len(lst) == 4, "Wrong number of digits (should be 4)"
        lst = list(map(int, lst))
        msg1 = struct.Struct('BBBBBB').pack(self.CMD_TM1637_DISPLAYHEX, tm_id, lst[0], lst[1], lst[2], lst[3])
        msg = [bytes(str(device), 'ascii'), 6, 0, msg1]
        self.send_msg(msg)

    # class: TM1637
    def TM1637DisplayBrightness(self, device, tm_id, brightness):
        """ Set display brightness"""
        assert (0 <= brightness <= 7), "Brightness should be between 0 and 7. 0 to clear the display"
        msg1 = struct.Struct('BBB').pack(self.CMD_TM1637_DISPLAY_BRIGHTNESS, tm_id, brightness)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: Liquid_Crystal_I2C
    def LiquidCrystalBegin(self, device, cols, rows):
        """ Connect to LiquidCrystal i2c chip """
        msg1 = struct.Struct('BBBB').pack(self.CMD_LIQUID_CRYSTAL_INIT, 0x27, cols, rows)
        msg = [bytes(str(device), 'ascii'), 4, 0, msg1]
        self.send_msg(msg)

    # class: Liquid_Crystal_I2C
    def LiquidCrystalBacklight(self, device, enable):
        """ LiquidCrystal backlight """
        msg1 = struct.Struct('BB').pack(self.CMD_LIQUID_CRYSTAL_BACKLIGHT, enable)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: Liquid_Crystal_I2C
    def LiquidCrystalBlink(self, device, enable):
        """ LiquidCrystal blink """
        msg1 = struct.Struct('BB').pack(self.CMD_LIQUID_CRYSTAL_BLINK, enable)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: Liquid_Crystal_I2C
    def LiquidCrystalCursor(self, device, col, row):
        """ LiquidCrystal set cursor """
        msg1 = struct.Struct('BBB').pack(self.CMD_LIQUID_CRYSTAL_CURSOR, col, row)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: Liquid_Crystal_I2C
    def LiquidCrystalPrint(self, device, message):
        """ LiquidCrystal print """
        if len(message) > 30:
            message = message[:30]
        if type(message) == type('a'):
            message = bytes(message, 'ascii')

        msg1 = struct.Struct('B' + str(len(message)) + 's').pack(self.CMD_LIQUID_CRYSTAL_PRINT, message)
        msg = [bytes(str(device), 'ascii'), 1 + len(message), 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerPlayFolder(self, device, player_id, folder_id, file_id):
        """ Play file from folder on DFPlayer """
        msg1 = struct.Struct('BBBB').pack(self.CMD_DFPLAYER_PLAYFOLDER, player_id, folder_id, file_id)
        msg = [bytes(str(device), 'ascii'), 4, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerVolume(self, device, player_id, volume):
        """ Set volume """
        msg1 = struct.Struct('BBB').pack(self.CMD_DFPLAYER_VOLUME, player_id, volume)
        msg = [bytes(str(device), 'ascii'), 3, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerBegin(self, device, player_id, rx_pin, tx_pin):
        """ Connect to DFPlayer """
        msg1 = struct.Struct('BBBB').pack(self.CMD_DFPLAYER_BEGIN, player_id, rx_pin, tx_pin)
        msg = [bytes(str(device), 'ascii'), 4, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerStart(self, device, player_id):
        """ Play """
        msg1 = struct.Struct('BB').pack(self.CMD_DFPLAYER_START, player_id)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerPause(self, device, player_id):
        """ Pause """
        msg1 = struct.Struct('BB').pack(self.CMD_DFPLAYER_PAUSE, player_id)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerStop(self, device, player_id):
        """ Stop """
        msg1 = struct.Struct('BB').pack(self.CMD_DFPLAYER_STOP, player_id)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: DFPlayer
    def DFPlayerEnd(self, device, player_id):
        """ Disconnect """
        msg1 = struct.Struct('BB').pack(self.CMD_DFPLAYER_END, player_id)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: CapSense
    def CapSense(self, device, tx_pin, rx_pin, samples, ms_timeout):
        """ Do capacitive sensing """
        start_time = time.time()
        msg1 = struct.Struct('BBBBB').pack(self.CMD_CAPSENSE_DO, tx_pin, rx_pin, samples, ms_timeout)
        msg = [bytes(str(device), 'ascii'), 5, 0, msg1]
        self.send_msg(msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 7:
                dr = list(struct.Struct('BBB').unpack(msg[3][:3]))
                if dr[0] in [self.ANS_CAPSENSE_DO]:
                    if dr[1] == tx_pin and dr[2] == rx_pin:
                        res = list(struct.Struct('I').unpack(msg[3][3:7]))
                        return res[0]

    # class: RFID
    def RFIDGetCard(self, device, pin):
        """ Get ID of currently seen RFID card """
        start_time = time.time()
        msg1 = struct.Struct('BB').pack(self.CMD_RFID_DO, pin)
        msg = [bytes(str(device), 'ascii'), 5, 0, msg1]
        self.send_msg(msg)
        resender = ResendMessageTimer(self, msg)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                resender.stop()
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 10:
                rstr = msg[3]
                dr = list(struct.Struct('BB').unpack(rstr[:2]))
                if dr[0] in [self.ANS_RFID_DO]:
                    if dr[1] == pin:
                        res = ""
                        i = 2
                        while i <= 9:
                            res += hex(rstr[i])[2:].zfill(2)
                            i += 1
                        resender.stop()
                        return res.upper()

    # class: Video
    def VideoPlayFile(self, device, remote_filename, seek_ms, repeat):
        """ Play a file from local filesystem """
        if len(remote_filename) > 100:
            print("Name too long")
            return
        msg1 = struct.Struct('B').pack(self.CMD_VIDEO_PLAYFILE)
        msg1 += struct.Struct('I').pack(int(seek_ms))
        msg1 += struct.Struct('B' + str(len(remote_filename) + 1) + 's').pack(int(repeat),
                                                                              bytes(remote_filename, 'ascii'))
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoPlayURL(self, device, url, seek_ms, repeat):
        """ Play a file from URL """
        if len(url) > 100:
            print("Name too long")
            return
        msg1 = struct.Struct('B').pack(self.CMD_VIDEO_PLAYURL)
        msg1 += struct.Struct('I').pack(int(seek_ms))
        msg1 += struct.Struct('B' + str(len(url) + 1) + 's').pack(int(repeat), bytes(url, 'ascii'))
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoPlay(self, device):
        """ Resume playing """
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_PLAYCURRENT)
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoStop(self, device):
        """ Stop playing """
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_STOP)
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoPause(self, device):
        """ Pause playing """
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_PAUSE)
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoSetVolume(self, device, volume):
        """ Set playing volume """
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_VOLUME)
        msg1.append(volume)
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoSeek(self, device, seek_ms):
        """ Seek player to a position in media """
        msg1 = struct.Struct('B').pack(self.CMD_VIDEO_SEEK)
        msg1 += struct.Struct('I').pack(int(seek_ms))
        msg = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg)

    # class: Video
    def VideoGetPosition(self, device):
        """ Get current media position """
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_GET_POSITION)
        msg2 = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg2)
        while True:
            msg = self.get_msg()
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                if msg[3][0] == self.ANS_VIDEO_POSITION:
                    val = list(struct.Struct('I').unpack(msg[3][1:5]))[0]
                    return val

    # class: Video
    def VideoGetLength(self, device):
        """ Get media length in ms """
        start_time = time.time()
        msg1 = bytearray(0)
        msg1.append(self.CMD_VIDEO_GET_LENGTH)
        msg2 = [bytes(str(device), 'ascii'), len(msg1), 0, msg1]
        self.send_msg(msg2)
        while True:
            msg = self.get_msg(start_time)
            if msg == None:
                continue
            if self.msg_is_offline(device, msg):
                return
            if msg[0] == bytes(str(device), 'ascii') and msg[1] >= 3:
                if msg[3][0] == self.ANS_VIDEO_LENGTH:
                    val = list(struct.Struct('I').unpack(msg[3][1:5]))[0]
                    return val

    # class: WS2812
    def WS2812Init(self, device, n, pin, n_leds):
        """ Connect to WS2812 """
        # n pin n_leds
        msg1 = struct.Struct('BBBB').pack(self.CMD_WS2812_INIT, n, pin, n_leds)
        msg = [bytes(str(device), 'ascii'), 4, 0, msg1]
        self.send_msg(msg)

    # class: WS2812
    def WS2812Set(self, device, n, index, r, g, b):
        """ Set color at index (0-255) """
        # n index_low index_high r g b
        msg1 = struct.Struct('BBBBBBB').pack(self.CMD_WS2812_SET, n, index % 256, index // 256, r, g, b)
        msg = [bytes(str(device), 'ascii'), 7, 0, msg1]
        self.send_msg(msg)

    # class: WS2812
    def WS2812Sync(self, device, n):
        """ Send data to WS2812 """
        msg1 = struct.Struct('BB').pack(self.CMD_WS2812_SYNC, n)
        msg = [bytes(str(device), 'ascii'), 2, 0, msg1]
        self.send_msg(msg)

    # class: WS2812
    def colorStrToRGB(self, c):
        """ Converts color from form #FF0102 to [255, 1, 2] """
        line = str(c)[1:]
        return [int(t, 16) for t in [line[0:2], line[2:4], line[4:6]]]

    # class: VLC
    def checkIfVlcRunning(self, player_id):
        """
        Check if there is running VLC process for selected port
        """
        # Iterate over the all the running process
        if str(player_id) not in "0123456789":
            raise ValueError
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if "vlc" in proc.name().lower():
                    cmd = proc.cmdline()
                    # ['vlc', '-I', 'rc', '--rc-host=0.0.0.0:9082'] example running vlc
                    if len(cmd) == 4 and cmd[3] == ("--rc-host=0.0.0.0:908" + str(player_id)):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    # class: VLC
    def startPlayer(self, player_id):
        """
        Starts player with id
        :param player_id: id of player. Specifies the listen port
        """
        subprocess.Popen(['sudo', '-u', 'pi', 'vlc', '-I', 'rc', '--rc-host=0.0.0.0:908' + str(player_id)])

    # class: VLC
    def ensurePlayerRunning(self, player_id):
        """
        Ensures that player is running
        :rtype: True if player was already running
        :param player_id:  id of player. Specifies the listen port
        """
        if not self.checkIfVlcRunning(player_id):
            self.startPlayer(player_id)
            return False
        return True

    # class: VLC
    def killAllPlayers(self):
        """
        Kills all running vls players
        """
        subprocess.call(['killall', 'vlc'])

    # class: VLC
    def connectToPlayer(self, player_id):
        """
        Creates interface for vlc player
        :param player_id: id of player. Specifies the listen port
        :return: Instance of player connection
        """
        if not self.ensurePlayerRunning(player_id):
            time.sleep(0.3)
        return Player(False, player_id)


class Player:
    def __init__(self, api, player_id, host="127.0.0.1"):
        self.api = api
        self.player_id = player_id
        self.dir = "/home/pi/sound"
        self.session = telnetlib.Telnet(host, 9080 + int(player_id), 100)

    # class: VLCConnection
    def playSound(self, name):
        """
        Plays sound from /home/pi/sound/$name
        :param name: name of mp3 file
        """
        self.session.write(("add " + self.dir + "/" + name + "\n").encode('ascii'))

    # class: VLCConnection
    def volume(self, volume):
        """
        Sets playback volume of player
        :param volume: 0..512
        """
        if volume < 0 or volume > 512:
            raise ValueError("Volume must be between 0 and 512")
        self.session.write(("volume " + str(volume) + "\n").encode('ascii'))

    # class: VLCConnection
    def pauseOrResume(self):
        """
        Toggles pause on playback
        """
        self.session.write("pause\n".encode('ascii'))

    # class: VLCConnection
    def stop(self):
        """
        Stop playback
        """
        self.session.write("stop\n".encode('ascii'))

    # class: VLCConnection
    def setLoop(self, enable):
        """
        Enables or disables loop playback
        :param enable: loop enable value
        """
        self.session.write(("repeat" + ("on" if enable else "off") + "\n").encode("ascii"))

    # class: VLCConnection
    def sendCommand(self, command):
        """
        Send abstract command to vlc instane
        :param command: general command to send to local vlc instance
        """
        self.session.write((command + "\n").encode("ascii"))


class ResendMessageTimer:
    api = None
    msg = None
    timer = None
    cancelled = False

    def __init__(self, api, msg):
        self.api = api
        self.msg = msg
        self.timer = Timer(0.1, self.send_message)
        self.timer.start()

    def send_message(self):
        try:
            if not self.cancelled:
                self.api.send_msg(self.msg)
        except:
            print("Failed in resend")
        finally:
            if not self.cancelled:
                self.timer = Timer(0.1, self.send_message)
                self.timer.start()

    def stop(self):
        self.cancelled = True
        try:
            self.timer.cancel()
        except:
            pass


def get_slot_safe(slot):
    if slot != -1:
        return slot
    try:
        slot = builtins.slot
    except:
        pass
    if slot != -1:
        return slot
    return 0
