class Cells {
  constructor(items, padding, attr = {}) {
    this.items = items;

    const cells = this.items.map(x => new BoxOutline(x, padding, attr));
    this.layout = new HStackLayout(cells, 0);
  }
  draw(svg) {
    return this.layout.draw(svg);
  }
}
