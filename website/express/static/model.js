class ChestnutModel {
  constructor(model, data) {
    this.tlds = Object.values(model).map(x => {
      const table = getTableFromPath(x.table);
      const { rows } = data[table];
      return getDS(x, data, rows);
    });
    this.layout = new VStackLayout(this.tlds, 20);
  }
  draw(svg, pos, meta) {
    return this.layout.draw(svg, pos, meta, 0);
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
  draw(svg, pos, meta) {
    checkArgs(svg, pos);

    return passCheckWH(this.layout.draw(svg, pos, meta));
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
  static allRecords = [];
  static pad = 5;

  constructor(model, data, row) {
    Record.allRecords.push(this);

    this.row = row;
    this.path = model.table;
    this.table = getTableFromPath(this.path);

    const { header, rows: allRows } = data[this.table];

    this.nested = (model.value && model.value.nested || [])
      .map(nestedModel => {
        const nestedRows = getNestedRows(data, header, row, nestedModel);
        return getDS(nestedModel, data, nestedRows)
      });

    // // Layout
    // const text = new Text(`id=${this.row[0]}`);
    this.vStack = new VStackLayout(this.nested, 5);
    this.color = getColorFromTable(this.table);
    // this.box = new Box(vStack, 5, { fill });

    this.group = document.createElementNS(xmlns, "g");
    this.textEl = createText(`id=${this.row[0]}`, Record.pad, Record.pad);
    this.group.appendChild(this.textEl);

    this.savedPos = null;
  }
  static async moveAllToSavedPos() {
    for (const record of Record.allRecords) {
      await promiseDelay(3000 / Record.allRecords.length);
      record.moveToSavedPos();
    }
  }
  moveToSavedPos() {
    const { x, y } = this.savedPos;
    this.group.setAttribute('transform', `translate(${x}, ${y})`);
  }
  draw(svg, pos, meta) {
    checkArgs(svg, pos);

    this.savedPos = pos;

    let { x, y } = pos;

    svg.prepend(this.group); // HACKY to get sizing.

    const textBBox = this.textEl.getBBox();

    x += Record.pad;
    y += 2 * Record.pad + textBBox.height; // HACKY.

    let { w, h } = this.vStack.draw(svg, { x, y }, meta);
    w = 2 * Record.pad + Math.max(w, textBBox.width);
    h += (this.nested.length ? 3 : 2) * Record.pad + textBBox.height;

    svg.prepend(this.group);

    if (0 === meta.state)
      this.group.setAttribute('transform', `translate(${-w - 200 * Math.random()}, ${-50 * Math.random()})`);
    else
      this.group.setAttribute('transform', `translate(${x}, ${y})`);

    this.group.prepend(createBox(0, 0, w, h, { fill: this.color }));

    return { w, h };
  }
}
