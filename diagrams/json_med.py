SCHEMA_JSON = {
  "0": {
    "keys": [
      {
        "path": [],
        "key": "id"
      }
    ],
    "value": {
      "type": "ptr",
      "target": 0
    },
    "table": "activity",
    "type": "Index",
    "id": 0,
    "condition": "id <= param[oldest]"
  },
  "1": {
    "table": "activity",
    "type": "BasicArray",
    "id": 0,
    "value": {
      "fields": [
        "id",
        "created_at",
        "updated_at",
        "action",
        "content",
        "channel_id",
        "user_id"
      ],
      "nested": [
        {
          "table": "activity.channel",
          "type": "BasicArray",
          "id": 0,
          "value": {
            "fields": [
              "id"
            ],
            "nested": []
          }
        }
      ]
    }
  },
  "2": {
    "table": "user",
    "type": "BasicArray",
    "id": 0,
    "value": {
      "fields": [
        "id",
        "username"
      ],
      "nested": []
    }
  }
}
