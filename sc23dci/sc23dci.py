"""
SC23DCI Module
Used for R/W access to the SC23DCI device and subscribe/publish to mqtt
"""
import json
import time
from datetime import datetime
from time import sleep
from env.env import Env

import paho.mqtt.client as mqtt
import requests as req
from loguru import logger


class ApiError(Exception):
    """
    Custom Exception for SC23DCI API errors
    """
    def __init__(self, status):
        self.status = status

    def __str__(self):
        return f"ApiError: status={self.status}"


class Wifi:
    """
    Represents Wi-Fi config of the SC23DCI device
    """
    essid = ""
    signal = 0
    password = True

    def __init__(self, wifi):
        self.essid = wifi['essid']
        self.signal = wifi['signal']
        self.password = wifi['password'] == 'true'

    def __eq__(self, other):
        if hasattr(other, 'essid'):
            return self.essid == other.essid
        return self.essid == other['essid']

    def __repr__(self):
        return f"(SSID: {self.essid}, Signal: {self.signal}, Password: {self.password})"


class SC23DCI:
    """
    Handles all the SC23DCI API polling and MQTT sub/pub
    """
    mqtt_client = 0
    mqtt_list = []
    req_base_url = 0
    set_point = 0
    working_mode = 0
    power_state = 0
    fan_speed = 0
    flap_rotate = 0
    timeplan_mode = 0
    temperature = 0
    night_mode = 0
    timer_status = 0
    heating_disabled = 0
    cooling_disabled = 0
    hotel_mode = 0
    uptime = 0
    software_version = 0
    date_time = datetime.now()
    uid = 0
    device_type = 0
    ip = 0
    subnet = 0
    gateway = 0
    dhcp = 0
    serial = 0
    name = 0
    wifi = []
    http_timeout = 5
    http_timeout_retry_count = 0
    unknown = []
    change_backlog = []

    def __init__(self, ip: str):
        self.req_base_url = f"http://{ip}/api/v/1/"
        self.refresh()

    def __repr__(self):
        return (
            f"SC23DCI\n"
            f"set_point:{self.set_point}\n"
            f"working_mode: {self.working_mode}\n"
            f"power_state: {self.power_state}\n"
            f"fan_speed: {self.fan_speed}\n"
            f"flap_rotate: {self.flap_rotate}\n"
            f"timeplan_mode: {self.timeplan_mode}\n"
            f"temperature: {self.temperature}\n"
            f"night_mode: {self.night_mode}\n"
            f"timer_status: {self.timer_status}\n"
            f"heating_disabled: {self.heating_disabled}\n"
            f"cooling_disabled: {self.cooling_disabled}\n"
            f"hotel_mode: {self.hotel_mode}\n"
            f"uptime: {self.uptime} seconds\n"
            f"software_version: {self.software_version}\n"
            f"dateTime: {self.date_time}\n"
            f"uid: {self.uid}\n"
            f"device_type: {self.device_type}\n"
            f"ip: {self.ip}\n"
            f"subnet: {self.subnet}\n"
            f"gateway: {self.gateway}\n"
            f"dhcp: {self.dhcp}\n"
            f"serial: {self.serial}\n"
            f"name: {self.name}\n"
            f"SSIDs: {self.wifi}\n"
            f"MqttClient: {self.mqtt_client}\n"
            f"MqttList: {self.mqtt_list}\n"
            f"unkown: {self.unknown}\n"
            f"backlog: {self.change_backlog}"
        )

    # http section
    def http_get(self, endpoint):
        """
        Getter for SC23DCI API endpoints
        :param endpoint: the endpoint of the API. eg.: status | network/scan
        :return: the response body as json or none
        """
        retries = 0
        while retries <= self.http_timeout_retry_count:
            try:
                res = req.get(self.req_base_url + endpoint, timeout=self.http_timeout)
                if res.status_code != 200:
                    logger.error(f"GET {endpoint} {res.status_code}")
                    # something went wrong.
                    raise ApiError(f"GET {endpoint} {res.status_code}")
                return res.json()
            except:
                logger.debug(f"Timeout on {self.req_base_url}{endpoint}")
                time.sleep(1)
                retries += 1
        logger.debug(f"Missed all timeout retries {self.req_base_url}{endpoint}")
        return None

    def http_post(self, endpoint, data=None):
        """
        Setter for SC23DCI API endpoints
        :param endpoint: the endpoint of the API. eg.: power/on
        :param data: the request body
        :return: the response body as json or none
        """
        retries = 0
        while retries <= self.http_timeout_retry_count:
            try:
                if data is not None:
                    res = req.post(
                        self.req_base_url + endpoint,
                        data=data,
                        timeout=self.http_timeout
                    )
                else:
                    res = req.post(
                        self.req_base_url + endpoint,
                        timeout=self.http_timeout
                    )
                if res.status_code != 200:
                    logger.error(f"POST {endpoint} {res.status_code}")
                    # This means something went wrong.
                    raise ApiError(f"POST {endpoint} {res.status_code}")
                # logger.debug("status: {}, response: {}", res.status_code, res.json())
                return res.json()
            except:
                logger.debug(
                    f"Timeout on POST {self.req_base_url}{endpoint}, data: {data}"
                )
                retries += 1
        logger.debug(f"Missed all timeout retries {self.req_base_url}{endpoint}, data: {data}")
        return None

    def refresh(self):
        """
        Polls new data from the device and updates this instance
        """
        self.unknown = []
        ret = self.http_get('status')
        if ret is not None:
            data = ret['RESULT']
            self.software_version = ret['sw']['V']
            self.uid = ret['UID']
            self.device_type = ret['deviceType']
            self.date_time = datetime(
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
            # temperature set point in °C
            self.set_point = data['sp']
            # working mode: heating(0), cooling(1), dehumidification(3), fan_only(4), auto(5)
            self.working_mode = data['wm']
            # power state: off: 0, on: 1
            self.power_state = data['ps']
            # fan speed: auto: 0, speeds: 1-3
            self.fan_speed = data['fs']
            # flap rotate: rotate: 0, fixed: 7
            self.flap_rotate = data['fr']
            # timeplan mode: off: 0, on: 1
            self.timeplan_mode = data['cm']
            # a? maybe related to timeplan_mode?
            self.unknown.append({"a": data['a']})
            # room temperature °C (integer)
            self.temperature = data['t']
            # cp? maybe state of the external relais input on the power terminals
            self.unknown.append({"cp": data['cp']})
            # night mode: off: 0, on: 1
            self.night_mode = data['nm']
            # ns?
            self.unknown.append({"ns": data['ns']})
            # cloudstatus?
            self.unknown.append({"cloudStatus": data['cloudStatus']})
            # connectionstatus?
            self.unknown.append({"connectionStatus": data['connectionStatus']})
            # cloudConfig?
            self.unknown.append({"cloudConfig": data['cloudConfig']})
            # the last configured working mode?
            self.unknown.append({"cfg_lastWorkingMode": data['cfg_lastWorkingMode']})
            # Timer active: 1, Timer inactive: 0
            self.timer_status = data['timerStatus']
            # heating: disabled = 1, enabled = 0
            self.heating_disabled = data['heatingDisabled']
            # cooling: disabled = 1, enabled = 0
            self.cooling_disabled = data['coolingDisabled']
            # hotel mode: off: 0, on: 1
            self.hotel_mode = data['hotelMode']
            # kl? Key Lock?
            self.unknown.append({"kl": data['kl']})
            # heating with heating resistance  off: 0, on: 1
            self.unknown.append({"heatingResistance": data['heatingResistance']})
            # inputFlags?
            self.unknown.append({"inputFlags": data['inputFlags']})
            # ncc?
            self.unknown.append({"ncc": data['ncc']})
            # pwd? maybe secure the api with pwd? how would auth work?
            self.unknown.append({"pwd": data['pwd']})
            # heap (free or used? kbytes or bytes?)
            self.unknown.append({"heap": data['heap']})
            # ccv?
            self.unknown.append({"ccv": data['ccv']})
            # cci?
            self.unknown.append({"cci": data['cci']})
            # daynumber (weekday? Sa: ?, Su: ?, Mo: ?, Tu: ?, We: ?, Th: ?, Fr: ?)
            self.unknown.append({"daynumber": data['daynumber']})
            # uptime of ??? maybe the Wi-Fi connection? seconds? updates in intervals of 5 seconds
            self.uptime = data['uptime']
            # uscm?
            self.unknown.append({"uscm": data['uscm']})
            # lastRefresh (data x ms old?)
            self.unknown.append({"lastRefresh": data['lastRefresh']})

            backlogs = self.change_backlog
            self.change_backlog = []
            for backlog in backlogs:
                if data[backlog['key']] != backlog['value']:
                    if backlog['arg'] is None:
                        backlog['func']()
                    else:
                        backlog['func'](backlog['arg'])

            if self.mqtt_client != 0 and len(self.mqtt_list) > 0:
                self.mqtt_publish()
        # logger.debug(self)

    def add_backlog(self, func, arg, key, value):
        """
        Adds a write request to the backlog.
        Will be removed when read value equals the written value.
        Backlog items that were not removed will be called again
        with the next refreshes until they are removed.
        :param func: The target function. eg.: self.set_working_mode
        :param arg: The argument for the function func
        :param key: The unique key to identify the item in the backlog
        :param value: The value to be written to the device
        """
        backlogs = self.change_backlog
        for backlog in backlogs:
            if backlog['func'] == func:
                self.change_backlog.remove(backlog)
        self.change_backlog.append({'func': func, 'arg': arg, 'key': key, 'value': value})

    def clear_ssids(self):
        """
        clears the ssid list
        """
        self.wifi = []

    def get_ssids(self):
        """
        API Getter for the Wi-Fi SSIDs
        :return: The List of SSIDs or None
        """
        ret = self.http_get('network/scan')
        data = ret['RESULT']
        if ret is None:
            return None
        for wifi in data:
            if wifi not in self.wifi:
                self.wifi.append(Wifi(wifi))
        return self.wifi

    def scan_ssids(self):
        """
        Scans Wi-Fi SSIDs using the API
        :return:
        """
        self.clear_ssids()
        for i in range(5):
            self.get_ssids()
            sleep(1)
        return self.wifi

    def switch_on(self):
        """
        Sends Power on request to the API
        """
        self.add_backlog(self.switch_on, None, 'ps', 1)
        ret = self.http_post('power/on')

    def switch_off(self):
        """
        Sends Power off request to the API
        """
        self.add_backlog(self.switch_off, None, 'ps', 0)
        ret = self.http_post('power/off')

    def set_temperature(self, set_point):
        """
        Sends temperature set point request to the API
        :param set_point: The target temperature in °C
        """
        set_point = round(
            max(
                min(
                    set_point,
                    Env.get_env('SC23DCI_MAX_TEMP_C')
                ),
                Env.get_env('SC23DCI_MIN_TEMP_C')
            )
        )
        self.add_backlog(self.set_temperature, set_point, 'sp', set_point)
        ret = self.http_post('set/setpoint', {'p_temp': set_point})

    def set_fan_speed(self, speed):
        """
        Sends fan speed request to the API
        :param speed: The fanspeed auto:0, speed: 1-3
        """
        speed = max(min(speed, 3), 0)
        self.add_backlog(self.set_fan_speed, speed, 'fs', speed)
        ret = self.http_post('set/fan', {'value': speed})

    def set_flap_rotation(self, rotate):
        """
        Sends flap rotation request to the API
        :param rotate: Rotate: 0, fixed: 7
        """
        mode = 0 if rotate else 7
        self.add_backlog(self.set_flap_rotation, rotate, 'fr', mode)
        ret = self.http_post('set/feature/rotation', {'value': mode})

    def set_night_mode(self, night):
        """
        Sends night mode request to the API
        :param night: Nightmode true: on, false: off
        """
        mode = 1 if night else 0
        self.add_backlog(self.set_night_mode, night, 'nm', mode)
        ret = self.http_post('set/feature/night', {'value': mode})

    def set_timeplan_mode(self, mode):
        """
        Sends timeplan mode request to the API
        :param mode: Timeplan mode true: on, false: off
        """
        endpoint = 'on' if mode else 'off'
        self.add_backlog(self.set_timeplan_mode, mode, 'cm', (1 if mode else 0))
        ret = self.http_post('set/calendar/' + endpoint)

    def set_working_mode(self, mode):
        """
        Sends working mode request to the API
        :param mode: the target working mode.
        heating:0, cooling:1, dehumidification:3, fan_only:4, auto:5"
        """

        endpoint = ['heating', 'cooling', '', 'dehumidification', 'fanonly', 'auto']
        if mode < 0 or mode == 2 or mode > 5:
            logger.warning(
                f"{mode} not allowed. heating:0, cooling:1, dehumidification:3, fan_only:4, auto:5"
            )
            return
        if self.power_state == 0:
            self.switch_on()
        self.add_backlog(self.set_working_mode, mode, 'wm', mode)
        ret = self.http_post('set/mode/' + endpoint[mode])

    def set_mode_auto(self):
        """
        Sends working mode auto request to the API
        """
        self.set_working_mode(5)

    def set_mode_fan_only(self):
        """
        Sends working mode fan only request to the API
        """
        self.set_working_mode(4)

    def set_mode_dehumidification(self):
        """
        Sends working mode dehumidify request to the API
        """
        self.set_working_mode(3)

    def set_mode_cooling(self):
        """
        Sends working mode cooling request to the API
        """
        self.set_working_mode(1)

    def set_mode_heating(self):
        """
        Sends working mode heating request to the API
        """
        self.set_working_mode(0)

    # mqtt section
    def mqtt_publish(self):
        """
        Publisher for MQTT
        """
        for pub in self.mqtt_list:
            if pub['_id'] == 'temperature':
                self.mqtt_client.publish(pub['topic'], payload=self.temperature)
            if pub['_id'] == 'powerstate':
                self.mqtt_client.publish(pub['topic'], payload=self.power_state)
            if pub['_id'] == 'all':
                all_payload = {
                    "set_point": self.set_point,
                    "working_mode": self.working_mode,
                    "power_state": self.power_state,
                    "mode": self.working_mode if self.power_state == 1 else 6,
                    "fan_speed": self.fan_speed,
                    "flap_rotate": self.flap_rotate,
                    "timeplan_mode": self.timeplan_mode,
                    "temperature": self.temperature,
                    "night_mode": self.night_mode,
                    "timer_status": self.timer_status,
                    "heating_disabled": self.heating_disabled,
                    "cooling_disabled": self.cooling_disabled,
                    "hotel_mode": self.hotel_mode,
                    "uptime": self.uptime,
                    "software_version": self.software_version,
                    "time": self.date_time.isoformat(),
                    "uid": self.uid,
                    "device_type": self.device_type,
                    "ip": self.ip,
                    "subnet": self.subnet,
                    "gateway": self.gateway,
                    "dhcp": self.dhcp,
                    "serial": self.serial,
                    "name": self.name,
                    "wifi": self.wifi,
                    "mqttSubList": self.mqtt_list
                }
                self.mqtt_client.publish(pub['topic'], payload=json.dumps(all_payload))

    def mqtt_on_connect(self, client, userdata, flags, rc):
        """
        MQTT on connect callback
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        logger.info(f"MQTT connected with result code {rc}")
        self.mqtt_subscribe_to_all_topics()
        self.mqtt_client.publish(Env.get_env('MQTT_TOPIC_LWT'), payload='online', retain=True)
        self.mqtt_home_assistant_autodiscover()

    def mqtt_on_disconnect(self, client, userdata, flags, rc):
        """
        MQTT on disconnect callback
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        :return:
        """
        logger.info(f"MQTT disconnected with result code {rc}")

    def set_mqtt_client(self, broker, port):
        """
        Sets up the MQTT client
        :param broker: the ip or hostname
        """
        self.mqtt_client = mqtt.Client()
        # self.mqtt_client.enable_logger(logger=logger)
        self.mqtt_client.on_connect = self.mqtt_on_connect
        self.mqtt_client.on_disconnect = self.mqtt_on_disconnect
        self.mqtt_client.will_set(Env.get_env('MQTT_TOPIC_LWT'), payload='offline', retain=True)
        self.mqtt_client.connect(broker, port)
        self.mqtt_client.loop_start()


    def mqtt_enable_publish(self, topic, _id):
        """
        Enables publishing for topic
        :param topic: The topic to enable publish on
        :param _id: The unique id of the topic
        """
        new_pub = {
            '_id': _id,
            'topic': topic
        }
        for pub in self.mqtt_list:
            if '_id' in pub:
                if pub['_id'] == _id:
                    self.mqtt_list.remove(pub)
        self.mqtt_list.append(new_pub)

    def mqtt_disable_publish(self, topic, _id):
        """
        Disables publishing for topic
        :param topic: The topic to disable publish on
        :param _id: The unique id of the topic
        """
        pub = {
            '_id': _id,
            'topic': topic
        }
        self.mqtt_list.remove(pub)

    def mqtt_enable_publish_temperature(self, topic):
        """
        Enables publishing of the temperature sensor
        :param topic: The topic to enable publish on
        """
        self.mqtt_enable_publish(topic, 'temperature')

    def mqtt_enable_publish_power_state(self, topic):
        """
        Enables publishing of the power state
        :param topic: The topic to enable publish on
        """
        self.mqtt_enable_publish(topic, 'powerstate')

    def mqtt_enable_publish_all(self, topic):
        """
        Enables publishing of the summary
        :param topic: The topic to enable publish on
        """
        self.mqtt_enable_publish(topic, 'all')

    def mqtt_subscribe_to_all_topics(self):
        if Env.get_env('MQTT_HASSIO_AUTODETECT'):
            def home_assistant_autodiscover_wrapper(client, userdata, msg):
                status = 'offline'
                try:
                    status = msg.payload.decode('utf-8')
                    if status == 'online':
                        self.mqtt_home_assistant_autodiscover()
                except (ValueError, TypeError) as e:
                    logger.error(e)
            self.mqtt_subscribe(
                'homeassistant/status',
                home_assistant_autodiscover_wrapper
            )
            self.mqtt_home_assistant_autodiscover()
        self.mqtt_subscribe(
            Env.get_env('MQTT_TOPIC_POWERSTATE_SET'),
            self.on_mqtt_power_state
        )
        self.mqtt_subscribe(
            Env.get_env('MQTT_TOPIC_MODE_SET'),
            self.on_mqtt_mode
        )
        self.mqtt_subscribe(
            Env.get_env('MQTT_TOPIC_SETPOINT_SET'),
            self.on_mqtt_setpoint
        )
        self.mqtt_subscribe(
            Env.get_env('MQTT_TOPIC_FLAP_MODE_SET'),
            self.on_mqtt_flap_mode
        )
        self.mqtt_subscribe(
            Env.get_env('MQTT_TOPIC_FAN_SPEED_SET'),
            self.on_mqtt_fan_speed
        )

    def mqtt_subscribe(self, topic, cb):
        """
        Enables subscribing to the topic and sets the callback
        :param topic: The topic to subscribe to
        :param cb: The callback function -> (client, userdata, msg)
        """
        self.mqtt_client.subscribe(topic)
        self.mqtt_client.message_callback_add(topic, cb)

    def on_mqtt_flap_mode(self, client, userdata, msg):
        """
        The callback of the flap mode setter subscribe
        :param client: The MQTT client
        :param userdata:
        :param msg: The message with payload
        """
        try:
            target_mode = int(float(msg.payload))
        except (ValueError, TypeError):
            target_mode = msg.payload.decode('utf-8')
        if target_mode == 'off':
            target_mode = 7
        elif target_mode == 'on':
            target_mode = 0
        self.set_flap_rotation(target_mode)
    def on_mqtt_fan_speed(self, client, userdata, msg):
        """
        The callback of the fan speed setter subscribe
        :param client: The MQTT client
        :param userdata:
        :param msg: The message with payload
        """
        try:
            target_speed = int(float(msg.payload))
        except (ValueError, TypeError):
            target_speed = msg.payload.decode('utf-8')
        match target_speed:
            case 'auto':
                target_speed = 0
            case 'low':
                target_speed = 1
            case 'medium':
                target_speed = 2
            case 'high':
                target_speed = 3
        self.set_fan_speed(target_speed)
    def on_mqtt_power_state(self, client, userdata, msg):
        """
        The callback of the power state setter subscribe
        :param client: The MQTT client
        :param userdata:
        :param msg: The message with payload
        """
        try:
            target_state = int(float(msg.payload))
        except (ValueError, TypeError):
            target_state = int(float(msg.payload.decode('utf-8')))
        match target_state:
            case 'off':
                target_state = 0
            case 'on':
                target_state = 1
        if int(float(target_state)) == 0:
            self.switch_off()
        else:
            self.switch_on()

    def on_mqtt_mode(self, client, userdata, msg):
        """
        The callback of the working mode setter subscribe
        :param client: The MQTT client
        :param userdata:
        :param msg: The message with payload
        """
        try:
            mode = int(float(msg.payload))
        except (ValueError, TypeError):
            mode = msg.payload.decode('utf-8')

        if mode == 'off' or mode == 6:
            self.switch_off()
            return
        endpoint = ['heating', 'cooling', '', 'dehumidification', 'fanonly', 'auto']
        if mode in endpoint:
            self.set_working_mode(endpoint.index(mode))

    def on_mqtt_setpoint(self, client, userdata, msg):
        """
        The callback of the temperature set point setter subscribe
        :param client: The MQTT client
        :param userdata:
        :param msg: The message with payload
        """
        try:
            self.set_temperature(int(float(msg.payload)))
        except (ValueError, TypeError):
            self.set_temperature(int(float(msg.payload.decode('utf-8'))))

    def mqtt_home_assistant_autodiscover(self):
        """
        Home assistant autodiscover publisher
        """
        if not Env.get_env('MQTT_HASSIO_AUTODETECT'):
            return
        discovery_prefix = Env.get_env('MQTT_HASSIO_TOPIC')
        component='climate'
        object_id=Env.get_env('MQTT_HASSIO_OBJECT_ID')
        config={
            'name': 'SC23DCI',
            'unique_id': object_id,
            'modes': ['heat', 'cool', 'dry', 'fan_only', 'auto', 'off'],
            'max_temp': float(Env.get_env('SC23DCI_MAX_TEMP_C')),
            'min_temp': float(Env.get_env('SC23DCI_MIN_TEMP_C')),
            'temperature_unit': 'C',
            'availability_topic': Env.get_env('MQTT_TOPIC_LWT'),
            'mode_command_topic': Env.get_env('MQTT_TOPIC_MODE_SET'),
            'mode_command_template': "{{"
                                     " ['heating', 'cooling', 'dehumidification', 'fanonly', 'auto', 'off']"
                                     "[['heat', 'cool', 'dry', 'fan_only', 'auto', 'off'].index(value)]"
                                     " if value in ['heat', 'cool', 'dry', 'fan_only', 'auto', 'off'] else value "
                                     "}}",
            'mode_state_topic': Env.get_env('MQTT_TOPIC_ALL'),
            'mode_state_template': "{{"
                                   " ['heat', 'cool', '', 'dry', 'fan_only', 'auto', 'off']"
                                   "[value_json.mode|int] if value_json.mode|int in [0, 1, 3, 4, 5, 6] else value "
                                   "}}",
            'swing_mode_state_topic': Env.get_env('MQTT_TOPIC_ALL'),
            'swing_mode_state_template': "{{"
                                   " ['on', '', '', '', '', '', '', 'off'][value_json.flap_rotate|int]"
                                       " if value_json.flap_rotate|int in [0, 7] else value "
                                   "}}",
            'swing_mode_command_topic': Env.get_env('MQTT_TOPIC_SETPOINT_SET'),
            'swing_mode_command_template': "{{ value }}",
            'fan_mode_state_topic': Env.get_env('MQTT_TOPIC_ALL'),
            'fan_mode_state_template': "{{"
                                       " ['auto', 'low', 'medium', 'high'][value_json.fan_speed|int]"
                                       " if value_json.fan_speed|int in [0, 1, 2, 3] else value "
                                       "}}",
            'fan_mode_command_topic': Env.get_env('MQTT_TOPIC_SETPOINT_SET'),
            'fan_mode_command_template': "{{ value }}",
            'temperature_command_topic': Env.get_env('MQTT_TOPIC_SETPOINT_SET'),
            'temperature_command_template': "{{ value }}",
            'temperature_state_topic': Env.get_env('MQTT_TOPIC_ALL'),
            'temperature_state_template': "{{ value_json.set_point }}",
            'current_temperature_topic': Env.get_env('MQTT_TOPIC_ALL'),
            'current_temperature_template': "{{ value_json.temperature }}",
            'sw_version': self.software_version
        }
        topic = f'{discovery_prefix}/{component}/{object_id}/config'
        self.mqtt_client.publish(topic, payload=json.dumps(config))
