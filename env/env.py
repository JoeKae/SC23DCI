"""
Environment variable Module
Grants read access to valid environment variable
"""
import os
from typing import Optional
from loguru import logger


class Env:
    """
    Env Class
    Provides the static getEnv method
    """

    validKeys = [
        'MQTT_BROKER_IP',
        'MQTT_TOPIC_TEMPERATURE',
        'MQTT_TOPIC_ALL',
        'MQTT_TOPIC_POWERSTATE',
        'MQTT_TOPIC_POWERSTATE_SET',
        'MQTT_TOPIC_MODE_SET',
        'MQTT_TOPIC_SETPOINT_SET',
        'SC23DCI_IP',
        'SC23DCI_POLL_INTERVAL'
    ]

    @staticmethod
    def get_env(key: str) -> Optional[str]:
        """
        Grants read access to valid environment variable
        :param key: The name of the variable to be read
        :raises Exception: 'Invalid env key requested'
        :return: The value of the Variable
        """

        if key not in Env.validKeys:
            raise Exception('Invalid env key requested')
        return os.getenv(key)

    @staticmethod
    def check_missing():
        """
        Checks for missing environment variables
        :raises Exception: Missing environment variables
        :return: A list of missing variable names
        """
        missing_envs = []
        for key in Env.validKeys:
            env_key = os.getenv(key)
            if env_key is None or env_key == '':
                missing_envs.append(key)
        for env in missing_envs:
            logger.error(f"Environment variable {env} is missing or invalid")
        if len(missing_envs) > 0:
            raise Exception('Missing environment variables')
