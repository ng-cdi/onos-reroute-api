# API for changing ONOS intents

## Usage:

Retrieving all installed intents: ```/api/get_intents```

Example of (just two for briefness) an intent:
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


Submitting a new intent(s): ```/api/push_intent```
See python example in testClient directory.

If the new intent is valid and accpeted by ONOS, a ```200``` code will be returned, otherwise a ```406``` code will be returned. 

Example of a valid new intent request:
```json
{
    "00:00:00:00:00:01/None00:00:00:00:00:07/None":[
        "00:00:00:00:00:01/None",
        "of:0000000000000001",
        "of:0000000000000007",
        "of:000000000000000c",
        "00:00:00:00:00:07/None"
    ]
}
```

Get routes between an access host and core host: ```/api/get_routes```

Example of a valid route request:
```json
{
    "key"  : "00:00:00:00:00:02/None00:00:00:00:00:08/None"
}
```

Example of a response, routes are listed from lowest hops to highest:
```json
{
   "0":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000009",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "1":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000007",
      "of:000000000000000c",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "2":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000008",
      "of:000000000000000c",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "3":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000009",
      "of:000000000000000c",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "4":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000007",
      "of:000000000000000c",
      "of:000000000000000e",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "5":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000008",
      "of:000000000000000c",
      "of:000000000000000e",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "6":[
      "00:00:00:00:00:02/None",
      "of:0000000000000002",
      "of:0000000000000009",
      "of:000000000000000c",
      "of:000000000000000e",
      "of:000000000000000d",
      "00:00:00:00:00:08/None"
   ],
   "key":"00:00:00:00:00:02/None00:00:00:00:00:08/None",
   "num_routes":"7"
}
```



