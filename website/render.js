let model = {
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
};

const COLORS_LEN = 16;
const COLORS = new Array(COLORS_LEN).fill().map((_, i) => {
  const rgb = hsluv.hsluvToRgb([ 70 * i % 360, 80, 90 ]);
  return '#' + rgb.map(x => (x * 255)|0)
    .map(x => x.toString(16).padStart(2, '0'))
    .join('');
});

const getColorFromTable = (() => {
  const colorTable = {};
  let i = 0;
  return function(tableName) {
    return colorTable[tableName] = colorTable[tableName] || COLORS[i++ % COLORS_LEN];
  };
})();

class ChestnutDiagram {
  constructor(model) {
    const items = Object.values(model).map(getDS);
    this.layout = new VStackLayout(items, 25);
  }
  draw(svg) {
    this.layout.draw(svg);
  }
}
