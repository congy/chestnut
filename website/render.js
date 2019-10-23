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

const xmlns = "http://www.w3.org/2000/svg";

function render_all(svg, model) {
  const elements = [];

  for (const [key, value] of Object.entries(model)) {
    const element = render_ds(svg, value);
    elements.push(element);
  }

  const { group, border } = helper_render_vstack(svg, elements, 10);
  return group;
}

function render_ds(svg, model) {
  const elements = [];

  {
    const text_table_name = document.createElementNS(xmlns, "text");
    elements.push(text_table_name);

    text_table_name.textContent = model.type + '[' + model.table + ']';
    text_table_name.setAttribute('dominant-baseline', 'hanging');
  }

  elements.push(...render_value(svg, model.value));

  const { group, border } = helper_render_vstack(svg, elements, 5);
  border.style.stroke = 'black';

  return group;
}

function render_value(svg, model) {
  const out = []

  {
    const text_fields = document.createElementNS(xmlns, "text");
    out.push(text_fields);
    text_fields.textContent = model.fields
        ? model.fields.join(', ')
        : model.type + '->' + model.target;
    text_fields.setAttribute('dominant-baseline', 'hanging');
  }

  if (model.nested) {
    for (const nested of model.nested) {
      out.push(render_ds(svg, nested));
    }
  }

  return out
}