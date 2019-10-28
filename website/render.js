let model = {
  "0": {
    "table": "lineitem_group5",
    "type": "BasicArray",
    "id": 0,
    "value": {
      "fields": [
        "id",
        "order_orderdate"
      ],
      "nested": [
        {
          "keys": [
            {
              "path": [],
              "key": "order.customer.nation.region.name"
            }
          ],
          "value": {
            "fields": [
              "id",
              "extendedprice",
              "discount"
            ],
            "nested": [
              {
                "table": "lineitems.supplier",
                "type": "BasicArray",
                "id": 0,
                "value": {
                  "fields": [
                    "id"
                  ],
                  "nested": [
                    {
                      "table": "supplier.nation",
                      "type": "BasicArray",
                      "id": 0,
                      "value": {
                        "fields": [
                          "id",
                          "name"
                        ],
                        "nested": []
                      }
                    }
                  ]
                }
              },
              {
                "table": "lineitems.part",
                "type": "BasicArray",
                "id": 0,
                "value": {
                  "fields": [
                    "id",
                    "p_type"
                  ],
                  "nested": []
                }
              }
            ]
          },
          "table": "lineitem_group5.lineitems",
          "type": "Index",
          "id": 0,
          "condition": "order.customer.nation.region.name == param[region_name]"
        }
      ]
    }
  },
  "1": {
    "table": "corder",
    "type": "BasicArray",
    "id": 0,
    "value": {
      "fields": [
        "id",
        "orderdate"
      ],
      "nested": []
    }
  },
  "2": {
    "keys": [
      {
        "path": [
          "lineitems"
        ],
        "key": "id"
      }
    ],
    "value": {
      "type": "ptr",
      "target": 0
    },
    "table": "corder",
    "type": "Index",
    "id": 0,
    "condition": "exists(lineitems, id == param[fk_lineitem_id])"
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
