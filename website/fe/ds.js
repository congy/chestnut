function getDS(model, data) {
  if ('Index' === model.type) return new IndexDS(model, data);
  if ('BasicArray' === model.type) return new ArrayDS(model, data);
  throw new Error(`Unknown type: '${model.type}'`);
}

class DS {
  constructor(model, data) {
    this.type = model.type;
    this.path = model.table;
    this.value = model.value;

    this.table = this.path.split('.').pop();
    this.color = getColorFromTable(this.table);

    const [ header, rows ] = data[this.table];

    const title = new TextElement(`${this.type}[${this.path}]`);

    const getNested = () => {
      const nestedItems = []
      for (const nested of this.value.nested || [])
        nestedItems.push(getDS(nested, data));
      return nestedItems.length
        ? new VStackLayout(nestedItems, 5)
        : new Spacer(10, 10);
    };

    const cellsItems = new Array(rows.length).fill().map(getNested);
    const cells = new Cells(cellsItems, 10, {
      'fill': this.color
    });

    this.layout = new VStackLayout([ title, cells ], 5);
  }
  draw(svg) {
    return this.layout.draw(svg);
  }
}

class ArrayDS extends DS {
  constructor(model, data) {
    super(model, data);
  }
}
class IndexDS extends DS {
  constructor(model, data) {
    super(model, data);
    this.pyramid = new PyramidOutline(this.layout, 10, {
      'fill': '#eeeeee',
    });
  }
  draw(svg) {
    return this.pyramid.draw(svg);
  }
}
