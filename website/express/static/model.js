class ChestnutModel {
  constructor(model, data) {
    this.tlds = Object.values(model).map(x => {
      const table = getTableFromPath(x.table);
      const { rows } = data[table];
      return getDS(x, data, rows);
    });
    this.layout = new VStackLayout(this.tlds, 20);
  }
  draw(svg) { // TODO pos arg.
    const pos = { x: 0, y: 0 };
    return this.layout.draw(svg, pos);
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

    let { header, rows: allRows } = data[this.table];
    this.rows = getRowSubsetByCondition([ header, rows ], model.condition);

    console.log(`${this.type}[${this.path}]: ${this.rows.length}/${allRows.length} rows.`);

    this.records = this.rows.map(row => new Record(model, data, row));
    this.layout = new HStackLayout(this.records, 0);
  }
  draw(svg, pos) {
    checkArgs(svg, pos);

    return passCheckWH(this.layout.draw(svg, pos));
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

    const { header, rows: allRows } = data[this.table];

    this.nested = (model.value && model.value.nested || [])
      .map(nestedModel => {
        const nestedRows = getNestedRows(data, header, row, nestedModel);
        return getDS(nestedModel, data, nestedRows)
      });

    // Layout
    const text = new Text(`id=${this.row[0]}`);
    const vStack = new VStackLayout([ text, ...this.nested ], 5);
    const fill = getColorFromTable(this.table);
    this.box = new Box(vStack, 5, { fill });
  }
  draw(svg, pos) {
    checkArgs(svg, pos);

    return passCheckWH(this.box.draw(svg, pos));
  }
}
