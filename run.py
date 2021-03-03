from scheduler import scheduler
from loguru import logger
from sc23dci import sc23dci
import configparser
import sys
import datetime

pwdPath = 'Path/To/Folder'
logger.remove()
logger.add(pwdPath+"logfile.log", rotation="500 KB", level="INFO")
logger.add(sys.stderr, level="INFO")
state = 100
try:
    logger.info('Service starting')
    if state == 100:
        try:
            logger.info('Config loading started')
            config = configparser.ConfigParser()
            config.read(pwdPath+'config.ini')
            state = 200
            logger.info('Config loading finished - State {}', state)
        except:
            state = 199
            logger.warning('Config loading error - ' + str(sys.exc_info()[1]))
    if state == 200:
        try:
            logger.info('Creating SC23DCI instance')
            ac = sc23dci.SC23DCI(config.get('SC23DCI', 'IP'))
            state = 300
            logger.info('SC23DCI instance created - State {}', state)
        except:
            state = 299
            logger.warning('SC23DCI instance could not be created')
    if state == 300:
        try:
            logger.info('Creating MqttClient instance')
            ac.setMqttClient(config.get('MQTT', 'BROKER'))
            ac.mqttEnablePublishTemperature(config.get('MQTT_TOPIC', 'TEMPERATURE'))
            ac.mqttEnablePublishPowerState(config.get('MQTT_TOPIC', 'POWERSTATE'))
            ac.mqttEnablePublishAll(config.get('MQTT_TOPIC', 'ALL'))
            ac.mqttSubscribeSetPowerstate(config.get('MQTT_TOPIC', 'POWERSTATE_SET'))
            ac.mqttSubscribeSetMode(config.get('MQTT_TOPIC', 'MODE_SET'))
            ac.mqttSubscribeSetSetpoint(config.get('MQTT_TOPIC', 'SETPOINT_SET'))
            state = 400
            logger.info('MqttClient instance created - State {}', state)
        except:
            state = 399
            logger.warning('MqttClient instance could not be created')
    if state == 400:
        try:
            logger.info('Scheduler initialization started')
            taskScheduler = scheduler.Scheduler().schedulerGenerator()
            job = taskScheduler.add_job(ac.refresh, 'interval', seconds=int(config.get('SCHEDULER', 'INTERVAL')),
                                        next_run_time=datetime.datetime.now())
            state = 500
            logger.info('Scheduler initialization finished - State {}', state)
        except:
            state = 499
            logger.warning('Scheduler initialization error - ' + str(sys.exc_info()[1]))
    if state == 500:
        try:
            logger.info('Service started successful')
            logger.info('Service is running')
            taskScheduler.start()
        except:
            pass
except:
    pass
