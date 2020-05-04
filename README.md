# API for changing ONOS intents

## HTML Endpoints:

### Submit Intent
Submit intent in structured language: `/` 

### User Overview
User overview table, detail usernames, user level and api_key hashed with sha256: `/user_table`

### SPP Overview
Service Protection Periods Overview - is SPP Enabled/Disabled, list installed SPPs with username, level, start time, end time, if it's enabled and whether it is currently active: `/spp_table`

## API Endpoints:

### Get Intents

Retrieving all installed intents: ```/api/get_intents```

Example of a valid POST request:
```json
{
    "api_key": "test_key"
}

Example of (just two for briefness) an intent response:
```json
{
  "routingList": [
    {
      "appId": {
        "id": 187,
        "name": "org.onosproject.ifwd"
      },
      "key": "00:00:00:00:00:01/None00:00:00:00:00:04/None",
      "paths": [
        {
          "path": [
            "00:00:00:00:00:01/None",
            "of:0000000000000001",
            "of:0000000000000008",
            "of:000000000000000c",
            "of:000000000000000a",
            "of:0000000000000004",
            "00:00:00:00:00:04/None"
          ],
          "weight": 1
        }
      ]
    },
    {
      "appId": {
        "id": 187,
        "name": "org.onosproject.ifwd"
      },
      "key": "00:00:00:00:00:05/None00:00:00:00:00:07/None",
      "paths": [
        {
          "path": [
            "00:00:00:00:00:05/None",
            "of:0000000000000005",
            "of:000000000000000a",
            "of:000000000000000c",
            "00:00:00:00:00:07/None"
          ],
          "weight": 1
        }
      ]
    }
  ]
}
```

### Post Intent(s)

Submitting a new intent(s): ```/api/push_intent```
See python example in testClient directory.

If the new intent is valid and accpeted by ONOS, a ```200``` code will be returned, otherwise a ```406``` code will be returned. If there is an SPP active a `409` will be returned, and the intent will be rejected. To override an SPP, you must submit an intent with a user api_key with a higher level than the current spp. See `get_spp` to see what SPP's are active, and at what priority they are. 

Example of a valid new intent request:
```json
{
    "api_key": "test_key",
    "routes":[
        {
            "key": "00:00:00:00:00:01/None00:00:00:00:00:07/None",
            "route": [
                "00:00:00:00:00:01/None",
                "of:0000000000000001",
                "of:0000000000000007",
                "of:000000000000000c",
                "00:00:00:00:00:07/None"
            ]
        }
    ]
} ]
}
```

### Get Routes

Get routes between an access host and core host: ```/api/get_routes```

Example of a valid route POST request:
```json
{
    "api_key": "test_key",
    "key"  : "00:00:00:00:00:02/None00:00:00:00:00:08/None"
}
```

Example of a response, routes are listed from lowest hops to highest:
```json
{
    "key": "00:00:00:00:00:02/None00:00:00:00:00:08/None",
    "num_routes": "7",
    "routes": {
        "0": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000009",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "1": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000007",
            "of:000000000000000c",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "2": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000008",
            "of:000000000000000c",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "3": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000009",
            "of:000000000000000c",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "4": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000007",
            "of:000000000000000c",
            "of:000000000000000e",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "5": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000008",
            "of:000000000000000c",
            "of:000000000000000e",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ],
        "6": [
            "00:00:00:00:00:02/None",
            "of:0000000000000002",
            "of:0000000000000009",
            "of:000000000000000c",
            "of:000000000000000e",
            "of:000000000000000d",
            "00:00:00:00:00:08/None"
        ]
    }
}
```

### Post SPP

Push SPP (service protection period):  `/api/push_spp`

``` json
{
    "api_key": "test_key",
    "spp":[
        {
            "priority": 10,
            "enabled": "True",
            "start_time": "2020-04-07T16:29:59+0000",
            "end_time": "2020-04-07T16:29:59+0000"
        }
    ]
}
```

### Is SPP

Is there an SPP active now? `/api/is_spp`

Example of a valid POST request:
```json
{
    "api_key": "test_key"
}
```

Example response:
``` json
{
    "spp": true
}
```

### Get SPP

Is there an SPP active now? `/api/get_spp`

Example of a valid POST request:
```json
{
    "api_key": "test_key"
}
```

Example response:
``` json
{
    "spp":[
        {
            "enabled": "True",
            "username": "Eleanor",
            "priority": 4,
            "start_time": "2020-04-07T16:29:59+0000",
            "end_time": "2020-04-07T16:29:59+0000",
            "uuid": "auuiddd"
        }
    ]
}
```

### Get Config

Get the currently installed config `/api/get_config`

Example of a valid POST request:
```json
{
    "api_key": "test_key"
}
```

Example response:
``` json
{
	"host" : "onos.com", 
	"port" : "80",
	"username" : "onos",
	"password" : "rocks" 
}
```

### Get Users

Get current users `/api/get_users`

Example of a valid POST request:
```json
{
    "api_key": "test_key"
}
```

Example response:
``` json
{
  "users": [
    {
      "hashed_api_key": "0d7bdf6ae4ec4bea34dc95d63ad83c052600b3c01afc35070d8a6a16573482ee",
      "level": 3,
      "username": "eleanor"
    },
    {
      "hashed_api_key": "f9e807cf5b1f3c5edea2a16c3cf8496808dd554845b4f6e86894156162c96b02",
      "level": 3,
      "username": "marco"
    },
    {
      "hashed_api_key": "92488e1e3eeecdf99f3ed2ce59233efb4b4fb612d5655c0ce9ea52b5a502e655",
      "level": 1,
      "username": "test"
    },
    {
      "hashed_api_key": "61436bd76a3920aefcae2b686344649de94ed276e4680a5f4340a048a92f4aa2",
      "level": 3,
      "username": "mehdi"
    }
  ]
}
```




