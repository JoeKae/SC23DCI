# SC23DCI HVAC REST API Documentation

The SC23DCI HVAC REST API has been reverse-engineered to enable seamless communication with compatible HVAC devices. 
The current state of the REST API is documented using Postman.

## Postman Documentation

The detailed documentation of the SC23DCI HVAC REST API can be found [here][1].

## Sample Response of the status endpoint

Below is a sample JSON response from the HVAC device:
<details>

```json
{
    "success": true,
    "sw": {
        "V": "1.0.42"
    },
    "UID": "fc:f5:a3:90:43:1b",
    "deviceType": "001",
    "time": {
        "d": 3,
        "m": 2,
        "y": 2024,
        "h": 20,
        "i": 21
    },
    "net": {
        "ip": "172.30.1.6",
        "sub": "255.255.0.0",
        "gw": "172.30.0.1",
        "dhcp": "1"
    },
    "setup": {
        "serial": "IN2037676",
        "name": "SC23DCI"
    },
    "RESULT": {
        "sp": 24,
        "wm": 0,
        "cfg_lastWorkingMode": 0,
        "ps": 0,
        "fs": 0,
        "fr": 7,
        "cm": 0,
        "a": [],
        "t": 21,
        "cp": 0,
        "nm": 0,
        "ns": 0,
        "cloudStatus": 4,
        "connectionStatus": 2,
        "cloudConfig": 1,
        "timerStatus": 0,
        "heatingDisabled": 0,
        "coolingDisabled": 0,
        "hotelMode": 0,
        "kl": 0,
        "heatingResistance": 0,
        "inputFlags": 0,
        "ncc": 0,
        "pwd": "",
        "heap": 11728,
        "ccv": 0,
        "cci": 0,
        "daynumber": 0,
        "uptime": 8665,
        "uscm": 0,
        "lastRefresh": 4242
    }
}
```
</details>

### Description of the keys

<details>

- **"sp"**: Temperature target/setpoint in °C
- **"wm"**: Working mode
  - 0: Heating
  - 1: Cooling
  - 3: Dehumidification
  - 4: Fan only
  - 5: Auto
- **"ps"**: Power state
  - 0: Off
  - 1: On
- **"fs"**: Fan speed
  - 0: Auto
  - 1: Low
  - 2: Medium
  - 3: High
- **"fr"**: Flap rotate
  - 0: Rotate
  - 7: Fixed
- **"cm"**: Timeplan/calendar mode, see [here][2]
  - 0: Off
  - 1: On
- **"a"**: Contains strings, e.g., "CP" when "cp" is 1
- **"t"**: Ambient temperature measured in °C
- **"cp"**: Control port see [here](#cp-control-port)
  - 0: CP ports are connected with each other
  - 1: CP ports are disconnected from each other
- **"nm"**: Night mode
  - 0: Off
  - 1: On
- **"ns"**: Unknown
- **"cloudStatus"**: Cloud-related status, unknown
- **"connectionStatus"**: Probably cloud-related connection status, unknown
- **"cloudConfig"**: Cloud-related configuration, unknown
- **"timerStatus"**: Timer status
  - 0: Inactive
  - 1: Active
- **"heatingDisabled"**: Heating disabled
  - 0: Off
  - 1: On
- **"coolingDisabled"**: Cooling disabled
  - 0: Off
  - 1: On
- **"hotelMode"**: Hotel mode
  - 0: Off
  - 1: On
- **"kl"**: Key lock (disable touch of the display)
  - 0: Off
  - 1: On
- **"heatingResistance"**: Electrical resistance heating
  - 0: Off
  - 1: On
- **"inputFlags"**: Unknown
- **"ncc"**: Unknown
- **"pwd"**: Password, unknown
- **"heap"**: Heap (free/used) in kilobytes or bytes.
- **"ccv"**: Unknown
- **"cci"**: Unknown
- **"daynumber"**: Unknown, always 0.
- **"uptime"**: Uptime in seconds, unknown of what
- **"uscm"**: Unknown
- **"lastRefresh"**: Last refresh data in milliseconds old
</details>

### CP (Control Port)

The JSON response includes a key named "cp" which corresponds to the 2 contacts on the electrical connectors of 
the HVAC device. When these connectors are connected, the "cp" value will be 0. If they are not connected, 
the "cp" value will be 1. The HVAC will only operate the heating or cooling when the "cp" connectors 
are connected with each other.

### Image of the CP connectors

<a href="../images/cp_contact_closeup.jpg">
    <img src="../images/cp_contact_closeup.jpg" style="width: 450px" alt="image of the cp connectors">
</a>

## ESP-01S

The ESP-01S module facilitates communication with the HVAC device via a serial connection, 
likely utilizing UART communication through the transmit (TX) and receive (RX) pins of the ESP-01S. 
By reverse-engineering this interface, it would become possible to develop a custom firmware for the ESP-01S or 
any other WiFi-enabled microcontroller. This enables the control of the HVAC device without relying on the 
agent provided by this project.


[1]: https://documenter.getpostman.com/view/32755199/2s9YyvCLb9
[2]: https://documenter.getpostman.com/view/32755199/2s9YyvCLb9#966436c8-4f93-4a03-baac-c15c21cb63f4