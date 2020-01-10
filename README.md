# API for changing ONOS intents

## Usage:

Retrieving all installed intents: ```/api/get_intents```

Submitting a new intent(s): ```/api/push_intent```
See python example in testClient directory.

If the new intent is valid and accpeted by ONOS, a ```200``` code will be returned, otherwise a ```406``` code will be returned. 

Example of a valid new intent request:
```json
{
    "00:00:00:00:00:02/None00:00:00:00:00:04/None":[
        "00:00:00:00:00:02/None",
        "of:0000000000000001",
        "of:0000000000000002",
        "00:00:00:00:00:04/None"
    ],
    "00:00:00:00:00:01/None00:00:00:00:00:03/None":[
        "00:00:00:00:00:01/None",
        "of:0000000000000001",
        "of:0000000000000003",
        "of:0000000000000002",
        "00:00:00:00:00:03/None"
    ]
}
```

