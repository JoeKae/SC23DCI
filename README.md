# SC23DCI
SC23DCI AC MQTT agent
Works with Devices like this one: https://www.frico.net/fileadmin/user_upload/frico/Pdf/cat_frico_soloclim_de.pdf

## Setup

### Activate Wi-Fi

While the A/C is running, long press the power icon on the display. After a few seconds you can cycle 
through ```[on, rst, off]``` by tapping the power icon. This sets Wi-Fi on/off or resets the WiFi-Config.
When the display shows the desired value, wait a few seconds and the setting is saved.

Entering this menu can be a bit tedious because the A/C tends to just turn off when the power icon is pressed.
You can try this:
Turn the A/C off, then double tap the power icon and do not lift your finger on the second tap.
I think it takes ~5 seconds until the menu appears. 

If you were successful, the A/C will create a WLAN, through which it can be configured using the [app](https://play.google.com/store/apps/details?id=it.kumbe.innovapp20) 
and can be integrated into your WLAN.

### Setup Wi-FI

Setup your Wi-Fi in your A/C unit using https://play.google.com/store/apps/details?id=it.kumbe.innovapp20

### Setup MQTT-Agent

1. Configure ```.env.file```
2. ```docker-compose up```

## Control the device via MQTT

### Set temperature

eg. set temperature to 20°C

If the configured topic is ```topic/ac/setpoint/set```

 Publish the payload ```20``` to ```topic/ac/setpoint/set```
 
### Set mode

eg. set mode to cooling

If the configured topic is ```topic/ac/mode/set```

Publish the payload ```1``` to ```topic/ac/mode/set```

0. heating
1. cooling
3. dehumidification
4. fan_only
5. auto
 
### Power device on/off

eg. turn device off (standby, Wi-Fi will still be up)

If the configured topic is ```topic/ac/powerstate/set```

Publish the payload ```0``` to ```topic/ac/powerstate/set```

0. Off
1. On
