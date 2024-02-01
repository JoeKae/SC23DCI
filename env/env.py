"""
Environment variable Module
Grants read access to valid environment variable
"""
import os

from loguru import logger


class Env:
    """
    Env Class
    Provides the static getEnv method
    """

    requiredKeys = [
        'MQTT_BROKER_IP',
        'SC23DCI_IP'
    ]

    optional_keys = {
        'MQTT_BROKER_PORT': 1883,
        'MQTT_TOPIC_TEMPERATURE': 'sc23dci/sensors/temperature/ac',
        'MQTT_TOPIC_ALL': 'sc23dci/all',
        'MQTT_TOPIC_POWERSTATE': 'sc23dci/powerstate',
        'MQTT_TOPIC_POWERSTATE_SET': 'sc23dci/powerstate/set',
        'MQTT_TOPIC_MODE_SET': 'sc23dci/mode/set',
        'MQTT_TOPIC_SETPOINT_SET': 'sc23dci/setpoint/set',
        'MQTT_TOPIC_FLAP_MODE': 'sc23dci/flap_mode',
        'MQTT_TOPIC_FLAP_MODE_SET': 'sc23dci/flap_mode/set',
        'MQTT_TOPIC_FAN_SPEED': 'sc23dci/fan_speed',
        'MQTT_TOPIC_FAN_SPEED_SET': 'sc23dci/fan_speed/set',
        'MQTT_TOPIC_LWT': 'sc23dci/lwt',
        'MQTT_HASSIO_AUTODETECT': True,
        'MQTT_HASSIO_OBJECT_ID': 'SC23DCI-unique-id-not-set',
        'MQTT_HASSIO_TOPIC': 'homeassistant',
        'SC23DCI_MAX_TEMP_C': 31,
        'SC23DCI_MIN_TEMP_C': 16,
        'SC23DCI_POLL_INTERVAL': 10
    }

    @staticmethod
    def get_env(key: str) -> str:
        """
        Grants read access to valid environment variable
        :param key: The name of the variable to be read
        :raises KeyError: 'Invalid env key requested'
        :return: The value of the Variable
        """

        if key not in Env.requiredKeys and key not in Env.optional_keys:
            raise KeyError('Invalid env key requested')
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        if key in Env.optional_keys:
            return str(Env.optional_keys[key])
        raise KeyError('Invalid env key requested')

    @staticmethod
    def check_missing():
        """
        Checks for missing environment variables
        :raises KeyError: Missing environment variables
        :return: A list of missing variable names
        """
        missing_envs = []
        for key in Env.requiredKeys:
            env_key = os.getenv(key)
            if env_key is None or env_key == '':
                missing_envs.append(key)
        for env in missing_envs:
            logger.error(f"Environment variable {env} is missing or invalid")
        if len(missing_envs) > 0:
            raise KeyError('Missing environment variables')
