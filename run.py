"""
Run Module
Starts up the agent
"""
import datetime
import sys

from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore
from loguru import logger

from env.env import Env
from sc23dci import sc23dci


def set_log_level(level):
    """
    Sets the logger to the given verbosity
    :param level: The verbosity
    - TRACE
    - DEBUG
    - INFO
    - SUCCESS
    - WARNING
    - ERROR
    - CRITICAL
    """
    if level not in ['TRACE', 'DEBUG', 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CRITICAL']:
        level = 'INFO'
    logger.remove()
    logger.add("/var/log/sc23dci.log", rotation="500 KB", level="INFO")
    logger.add(sys.stderr, level=level)


if __name__ == '__main__':
    set_log_level(Env.get_env('LOG_LEVEL'))
    Env.check_missing()

    logger.info('Creating SC23DCI instance')
    ac = sc23dci.SC23DCI(Env.get_env('SC23DCI_IP'))

    logger.info('Creating MqttClient instance')
    ac.set_mqtt_client(Env.get_env('MQTT_BROKER_IP'), Env.get_env('MQTT_BROKER_PORT'))
    ac.mqtt_enable_publish_temperature(Env.get_env('MQTT_TOPIC_TEMPERATURE'))
    ac.mqtt_enable_publish_power_state(Env.get_env('MQTT_TOPIC_POWERSTATE'))
    ac.mqtt_enable_publish_all(Env.get_env('MQTT_TOPIC_ALL'))

    logger.info('Scheduler initialization started')
    taskScheduler = scheduler = BlockingScheduler(daemon=True)
    job = taskScheduler.add_job(
        ac.refresh,
        'interval',
        seconds=int(Env.get_env('SC23DCI_POLL_INTERVAL')),
        next_run_time=datetime.datetime.now()
    )

    logger.info('Service started successful')
    logger.info('Service is running')
    taskScheduler.start()
