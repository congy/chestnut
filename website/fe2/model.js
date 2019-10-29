class ChestnutModel {
  constructor(model, data) {
    this.tlds = Object.values(model).map(x => {
      const table = getTableFromPath(x.table);
      const [ , rows ] = data[table];
      return getDS(x, data, rows);
    });
  }
  draw(svg) {
    let els = this.tlds.map((ds, i) => ds.draw(svg, 0, i));
    return vStackLayout(svg, els, 10);
  }
}

function getDS(model, data, rows) {
  if ('Index' === model.type) return new IndexDS(model, data, rows);
  if ('BasicArray' === model.type) return new ArrayDS(model, data, rows);
  throw new Error(`Unknown type: '${model.type}'`);
}

class DS {
  constructor(model, data, rows) {
    if (!Array.isArray(rows))
      throw Error(`ROWS NOT ARRAY: ${rows}.`);

    this.type = model.type;
    this.path = model.table;
    this.value = model.value;

    this.table = getTableFromPath(this.path);
    this.color = getColorFromTable(this.table);

    this.condition = model.condition;

    let [ header, allRows ] = data[this.table];
    this.rows = getRowSubsetByCondition([ header, rows ], model.condition);

    console.log(`${this.type}[${this.path}]: ${this.rows.length}/${data[this.table][1].length} rows.`);

    this.records = this.rows.map(row => new Record(model, data, row));
  }
  draw(svg, depth, nth) {
    const recordEls = this.records.map((r, i) => r.draw(svg, depth + 1, i));

    let hStack = hStackLayout(svg, recordEls, 0);

    if (depth && nth)
      return hStack; // Do not show text on lower depth.

    const text = drawTextElem(svg, `${this.type}[${this.path}]: ${this.condition || '(all)'}`);

    return vStackLayout(svg, [ text, hStack ], 5);
  }
}
class ArrayDS extends DS {
  // constructor(model, data, rows) {
  //   super(model, data, rows);
  // }
}
class IndexDS extends DS {
  // constructor(model, data, rows) {
  //   super(model, data, rows);
  // }
}


class Record {
  constructor(model, data, row) {
    this.row = row;
    this.path = model.table;
    this.table = getTableFromPath(this.path);

    const [ header, allRows ] = data[this.table];

    this.nested = (model.value && model.value.nested || [])
      .map(nestedModel => {
        const nestedRows = getNestedRows(data, header, row, nestedModel);
        return getDS(nestedModel, data, nestedRows)
      });
  }
  draw(svg, depth, nth) {
    const text = drawTextElem(svg, `id=${this.row[0]}`);

    const nestedElems = this.nested.map((n, i) => n.draw(svg, depth, nth));

    const vStack = vStackLayout(svg, [ text, ...nestedElems ], 5);

    const fill = getColorFromTable(this.table);
    return drawBox(svg, vStack, 5, { fill });
  }
}
