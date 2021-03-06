# encoding=utf8
from time import sleep
from datetime import datetime
from loguru import logger
import requests as req
import paho.mqtt.client as mqtt
import json


class ApiError(Exception):
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "ApiError: status={}".format(self.status)


class Wifi:
    essid = "",
    signal = 0,
    password = True

    def __init__(self, wifi):
        self.essid = wifi['essid']
        self.signal = wifi['signal']
        self.password = (wifi['password'] == 'true')

    def __eq__(self, other):
        if hasattr(other, 'essid'):
            return self.essid == other.essid
        else:
            return self.essid == other['essid']

    def __repr__(self):
        return "(SSID: {}, Signal: {}, Password: {})".format(self.essid, self.signal, self.password)


class SC23DCI:
    mqttClient = 0
    mqttList = []
    reqBaseurl = 0
    setPoint = 0
    workingMode = 0
    powerState = 0
    fanSpeed = 0
    flapRotate = 0
    timeplanMode = 0
    temperature = 0
    nightMode = 0
    timerStatus = 0
    heatingDisabled = 0
    coolingDisabled = 0
    hotelMode = 0
    uptime = 0
    softwareVersion = 0
    dateTime = datetime.now()
    UID = 0
    deviceType = 0
    ip = 0
    subnet = 0
    gateway = 0
    dhcp = 0
    serial = 0
    name = 0
    wifi = []
    httpTimeout = 5
    httpTimeoutRetryCount = 0
    unknown = []
    changeBacklog = []

    def __init__(self, ip: str):
        self.reqBaseurl = 'http://' + ip + '/api/v/1/'
        self.refresh()

    def __repr__(self):
        ret = "SC23DCI\nsetPoint:{}\nworkingMode: {}\npowerState: {}\nfanSpeed: {}\nflapRotate: {}\ntimeplanMode: {}\
        \ntemperature: {}\nnightMode: {}\ntimerStatus: {}\nheatingDisabled: {}\ncoolingDisabled: {}\nhotelMode: {}\
        \nuptime: {} seconds\nsoftwareVersion: {}\ndateTime: {}\nUID: {}\ndeviceType: {}\nip: {}\nsubnet: {}\
        \ngateway: {}\ndhcp: {}\nserial: {}\nname: {}\nSSIDs: {}\nMqttClient: {}\nMqttList: {}\nunkown: {}\
        \nbacklog: {}".format(
            self.setPoint, self.workingMode, self.powerState, self.fanSpeed, self.flapRotate, self.timeplanMode,
            self.temperature, self.nightMode, self.timerStatus, self.heatingDisabled, self.coolingDisabled,
            self.hotelMode, self.uptime, self.softwareVersion, self.dateTime.isoformat(), self.UID, self.deviceType,
            self.ip, self.subnet, self.gateway, self.dhcp, self.serial, self.name, self.wifi, self.mqttClient,
            self.mqttList, self.unknown, self.changeBacklog)
        return ret

    # http section
    def httpGet(self, endpoint):
        retries = 0
        while retries <= self.httpTimeoutRetryCount:
            try:
                res = req.get(self.reqBaseurl + endpoint, timeout=self.httpTimeout)
                if res.status_code != 200:
                    logger.error('GET {} {}'.format(endpoint, res.status_code))
                    # This means something went wrong.
                    raise ApiError('GET {} {}'.format(endpoint, res.status_code))
                # logger.debug("status: {}, response: {}", res.status_code, res.json())
                return res.json()
            except:
                logger.debug("Timeout on {}{}".format(self.reqBaseurl, endpoint))
                retries += 1
        logger.debug("Missed all timeout retries {}{}".format(self.reqBaseurl, endpoint))

    def httpPost(self, endpoint, data=None):
        retries = 0
        while retries <= self.httpTimeoutRetryCount:
            try:
                if data is not None:
                    res = req.post(self.reqBaseurl + endpoint, data=data, timeout=self.httpTimeout)
                else:
                    res = req.post(self.reqBaseurl + endpoint, timeout=self.httpTimeout)
                if res.status_code != 200:
                    logger.error('POST {} {}'.format(endpoint, res.status_code))
                    # This means something went wrong.
                    raise ApiError('POST {} {}'.format(endpoint, res.status_code))
                # logger.debug("status: {}, response: {}", res.status_code, res.json())
                return res.json()
            except:
                logger.debug("Timeout on POST {}{}, data: {}".format(self.reqBaseurl, endpoint, data))
                retries += 1
        logger.debug("Missed all timeout retries {}{}, data: {}".format(self.reqBaseurl, endpoint, data))

    def refresh(self):
        self.unknown = []
        ret = self.httpGet('status')
        if ret is not None:
            data = ret['RESULT']
            self.softwareVersion = ret['sw']['V']
            self.UID = ret['UID']
            self.deviceType = ret['deviceType']
            self.dateTime = datetime(
                day=ret['time']['d'],
                month=ret['time']['m'],
                year=ret['time']['y'],
                hour=ret['time']['h'],
                minute=ret['time']['i']
                )
            self.ip = ret['net']['ip']
            self.subnet = ret['net']['sub']
            self.gateway = ret['net']['gw']
            self.dhcp = ret['net']['dhcp']
            self.serial = ret['setup']['serial']
            self.name = ret['setup']['name']
            self.setPoint = data['sp']  # set temperature
            self.workingMode = data['wm']  # mode: heating(0), cooling(1), dehumidification(3), fan_only(4), auto(5)
            self.powerState = data['ps']  # off: 0, on: 1
            self.fanSpeed = data['fs']  # Auto: 0, speeds: 1-3
            self.flapRotate = data['fr']  # rotate: 0, fixed: 7
            self.timeplanMode = data['cm']  # off: 0, on: 1
            self.unknown.append({"a": data['a']})  # a?
            self.temperature = data['t']  # room temperature °C (integer)
            self.unknown.append({"cp": data['cp']})  # cp?
            self.nightMode = data['nm']  # off: 0, on: 1
            self.unknown.append({"ns": data['ns']})  # ns?
            self.unknown.append({"cloudStatus": data['cloudStatus']})  # cloudstatus?
            self.unknown.append({"connectionStatus": data['connectionStatus']})  # connectionstatus?
            self.unknown.append({"cloudConfig": data['cloudConfig']})  # cloudConfig?
            self.unknown.append({"cfg_lastWorkingMode": data['cfg_lastWorkingMode']})
            self.timerStatus = data['timerStatus']  # Timer active: 1, Timer inactive: 0
            self.heatingDisabled = data['heatingDisabled']  # 0/1
            self.coolingDisabled = data['coolingDisabled']  # 0/1
            self.hotelMode = data['hotelMode']  # off: 0, on: 1
            self.unknown.append({"kl": data['kl']})  # kl?
            self.unknown.append({"heatingResistance": data['heatingResistance']})  # heating with heating resistance  off: 0, on: 1
            self.unknown.append({"inputFlags": data['inputFlags']})  # inputFlags?
            self.unknown.append({"ncc": data['ncc']})  # ncc?
            self.unknown.append({"pwd": data['pwd']})  # pwd?
            self.unknown.append({"heap": data['heap']})  # heap (free or used? kbytes or bytes?)
            self.unknown.append({"ccv": data['ccv']})  # ccv?
            self.unknown.append({"cci": data['cci']})  # cci?
            self.unknown.append({"daynumber": data['daynumber']})  # daynumber (weekday? Sa: 0, Su: ?, Mo: ?, Tu: ?, We: ?, Th: ?, Fr: ?)
            self.uptime = data['uptime']  # uptime of wifi? seconds? intervals: 5
            self.unknown.append({"uscm": data['uscm']})  # uscm?
            self.unknown.append({"lastRefresh": data['lastRefresh']})  # lastRefresh (data x ms old?)

            backlogs = self.changeBacklog
            self.changeBacklog = []
            for backlog in backlogs:
                if data[backlog['key']] != backlog['value']:
                    if backlog['arg'] is None:
                        backlog['func']()
                    else:
                        backlog['func'](backlog['arg'])

            if self.mqttClient != 0 and len(self.mqttList) > 0:
                self.mqttPublish()
        # logger.debug(self)

    def addBacklog(self, func, arg, key, value):
        backlogs = self.changeBacklog
        for backlog in backlogs:
            if backlog['func'] == func:
                self.changeBacklog.remove(backlog)
        self.changeBacklog.append({'func': func, 'arg': arg, 'key': key, 'value': value})

    def clearSSIDs(self):
        self.wifi = []

    def getSSIDs(self):
        ret = self.httpGet('network/scan')
        data = ret['RESULT']
        if ret is None:
            return
        for wifi in data:
            if wifi not in self.wifi:
                self.wifi.append(Wifi(wifi))
        return self.wifi

    def scanSSIDs(self):
        self.clearSSIDs()
        for i in range(5):
            self.getSSIDs()
            sleep(1)
        return self.wifi

    def switchOn(self):
        self.addBacklog(self.switchOn, None, 'ps', 1)
        ret = self.httpPost('power/on')

    def switchOff(self):
        self.addBacklog(self.switchOff, None, 'ps', 0)
        ret = self.httpPost('power/off')

    def setTemperature(self, setPoint):
        setPoint = round(max(min(setPoint, 31), 16))
        self.addBacklog(self.setTemperature, setPoint, 'sp', setPoint)
        ret = self.httpPost('set/setpoint', {'p_temp': setPoint})

    def setFanSpeed(self, speed):
        speed = max(min(speed, 3), 0)
        self.addBacklog(self.setFanSpeed, speed, 'fs', speed)
        ret = self.httpPost('set/fan', {'value': speed})

    def setFlapRotation(self, rotate):
        mode = 0 if rotate else 7
        self.addBacklog(self.setFlapRotation, rotate, 'fr', mode)
        ret = self.httpPost('set/feature/rotation', {'value': mode})

    def setNightMode(self, night):
        mode = 1 if night else 0
        self.addBacklog(self.setNightMode, night, 'nm', mode)
        ret = self.httpPost('set/feature/night', {'value': mode})

    def setTimeplanMode(self, mode):
        endpoint = 'on' if mode else 'off'
        self.addBacklog(self.setTimeplanMode, mode, 'cm', (1 if mode else 0))
        ret = self.httpPost('set/calendar/' + endpoint)

    def setWorkingMode(self, mode):
        if mode < 0 or mode == 2 or mode > 5:
            logger.warning("{} not allowed. heating:0, cooling:1, dehumidification:3, fan_only:4, auto:5", mode)
            return
        endpoint = ['heating', 'cooling', '', 'dehumidification', 'fanonly', 'auto']
        self.addBacklog(self.setWorkingMode, mode, 'wm', mode)
        ret = self.httpPost('set/mode/' + endpoint[mode])

    def setModeAuto(self):
        self.setWorkingMode(5)

    def setModeFanOnly(self):
        self.setWorkingMode(4)

    def setModeDehumidification(self):
        self.setWorkingMode(3)

    def setModeCooling(self):
        self.setWorkingMode(1)

    def setModeHeating(self):
        self.setWorkingMode(0)

    # mqtt section
    def mqttPublish(self):
        for pub in self.mqttList:
            if pub['id'] == 'temperature':
                self.mqttClient.publish(pub['topic'], payload=self.temperature)
            if pub['id'] == 'powerstate':
                self.mqttClient.publish(pub['topic'], payload=self.powerState)
            if pub['id'] == 'all':
                allPayload = {
                    "setPoint": self.setPoint,
                    "workingMode": self.workingMode,
                    "powerState": self.powerState,
                    "fanSpeed": self.fanSpeed,
                    "flapRotate": self.flapRotate,
                    "timeplanMode": self.timeplanMode,
                    "temperature": self.temperature,
                    "nightMode": self.nightMode,
                    "timerStatus": self.timerStatus,
                    "heatingDisabled": self.heatingDisabled,
                    "coolingDisabled": self.coolingDisabled,
                    "hotelMode": self.hotelMode,
                    "uptime": self.uptime,
                    "softwareVersion": self.softwareVersion,
                    "time": self.dateTime.isoformat(),
                    "UID": self.UID,
                    "deviceType": self.deviceType,
                    "ip": self.ip,
                    "subnet": self.subnet,
                    "gateway": self.gateway,
                    "dhcp": self.dhcp,
                    "serial": self.serial,
                    "name": self.name,
                    "wifi": self.wifi,
                    "mqttSubList": self.mqttList
                }
                self.mqttClient.publish(pub['topic'], payload=json.dumps(allPayload))

    def mqttOnConnect(self, client, userdata, flags, rc):
        logger.info("MQTT connected with result code {}".format(rc))

    def mqttOnDisconnect(self, client, userdata, flags, rc):
        logger.info("MQTT disconnected with result code {}".format(rc))

    def setMqttClient(self, broker):
        self.mqttClient = mqtt.Client()
        # self.mqttClient.enable_logger(logger=logger)
        self.mqttClient.on_connect = self.mqttOnConnect
        self.mqttClient.on_disconnect = self.mqttOnDisconnect
        try:
            self.mqttClient.connect(broker)
            self.mqttClient.loop_start()
        except:
            logger.error("MQTT connection failed")

    def mqttEnablePublish(self, topic, id):
        new_pub = {
            'id': id,
            'topic': topic
        }
        for pub in self.mqttList:
            if 'id' in pub:
                if pub['id'] == id:
                    self.mqttList.remove(pub)
        self.mqttList.append(new_pub)

    def mqttDisablePublish(self, topic, id):
        pub = {
            'id': id,
            'topic': topic
        }
        self.mqttList.remove(pub)

    def mqttEnablePublishTemperature(self, topic):
        self.mqttEnablePublish(topic, 'temperature')

    def mqttEnablePublishPowerState(self, topic):
        self.mqttEnablePublish(topic, 'powerstate')

    def mqttEnablePublishAll(self, topic):
        self.mqttEnablePublish(topic, 'all')

    def mqttSubscribeSetPowerstate(self, topic):
        self.mqttClient.subscribe(topic)
        self.mqttClient.message_callback_add(topic, self.onMqttPowerState)

    def mqttSubscribeSetMode(self, topic):
        self.mqttClient.subscribe(topic)
        self.mqttClient.message_callback_add(topic, self.onMqttMode)

    def mqttSubscribeSetSetpoint(self, topic):
        self.mqttClient.subscribe(topic)
        self.mqttClient.message_callback_add(topic, self.onMqttSetpoint)

    def onMqttPowerState(self, client, userdata, msg):
        if int(float(msg.payload)) == 0:
            self.switchOff()
        else:
            self.switchOn()

    def onMqttMode(self, client, userdata, msg):
        self.setWorkingMode(int(float(msg.payload)))

    def onMqttSetpoint(self, client, userdata, msg):
        self.setTemperature(int(float(msg.payload)))
