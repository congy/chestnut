function getDS(model) {
  if ('Index' === model.type) return new IndexDS(model);
  if ('BasicArray' === model.type) return new ArrayDS(model);
  throw new Error(`Unknown type: '${model.type}'`);
}

class DS {
  constructor(model) {
    this.type = model.type;
    this.table = model.table;
    this.value = model.value;

    this.color = getColorFromTable(this.table.split('.').pop());

    const title = new TextElement(`${this.type}[${this.table}]`);

    const getNested = () => {
      const nestedItems = []
      for (const nested of this.value.nested || [])
        nestedItems.push(getDS(nested));
      return nestedItems.length
        ? new VStackLayout(nestedItems, 5)
        : new Spacer(10, 10);
    };

    const cellsItems = new Array(5).fill().map(getNested);
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
  constructor(model) {
    super(model);
  }
}
class IndexDS extends DS {
  constructor(model) {
    super(model);
    this.pyramid = new PyramidOutline(this.layout, 10, {
      'fill': '#eeeeee',
    });
  }
  draw(svg) {
    return this.pyramid.draw(svg);
  }
}
