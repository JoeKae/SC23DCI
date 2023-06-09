# SC23DCI
SC23DCI AC MQTT agent
Works with Devices like this one: https://www.frico.net/fileadmin/user_upload/frico/Pdf/cat_frico_soloclim_de.pdf

## Setup

1. Setup your Wi-Fi in your A/C unit using https://play.google.com/store/apps/details?id=it.kumbe.innovapp20
2. Configure ```.env.file```
3. ```docker-compose up```

## Control the device over MQTT

### Set temperature

eg. set temperature to 20°C

If the configured topic is ```topic/ac/powerstate/set```

 Publish the payload ```20``` to ```topic/ac/powerstate/set```
 
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
