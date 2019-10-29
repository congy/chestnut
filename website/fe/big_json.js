let x = {
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