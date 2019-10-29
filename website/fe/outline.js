class Outline {
  constructor(child, padding, attr = {}) {
    this.child = child;
    this.padding = padding;
    this.attr = attr;
  }
  getOutline(bbox) {
    throw Error('NOT IMPLEMENTED!');
  }
  draw(svg) {
    const group = document.createElementNS(xmlns, "g");
    svg.appendChild(group);

    const childEl = this.child.draw(svg);
    group.appendChild(childEl);

    childEl.setAttribute('transform', `translate(${this.padding}, ${this.padding})`);

    const bbox = childEl.getBBox();

    const outline = this.getOutline(bbox);
    group.appendChild(outline);
    group.appendChild(childEl);

    for (let kv of Object.entries(this.attr)) {
      outline.setAttribute(...kv);
    }

    return group;
  }
}

class BoxOutline extends Outline {
  constructor(child, padding, attr = {}) {
    super(child, padding, attr);
  }
  getOutline(bbox) {
    const box = document.createElementNS(xmlns, "rect");
    box.setAttribute('fill', 'white');
    box.setAttribute('stroke', 'black');
    box.setAttribute('width', bbox.width + 2 * this.padding);
    box.setAttribute('height', bbox.height + 2 * this.padding);
    return box;
  }
}

class PyramidOutline extends Outline {
  constructor(child, padding, attr = {}) {
    super(child, padding, attr);
  }
  getOutline(bbox) {
    const tri = document.createElementNS(xmlns, "polygon");
    tri.setAttribute('fill', 'white');
    tri.setAttribute('stroke', 'black');
    const points = [
      [0, bbox.height + 2 * this.padding],
      [bbox.width / 2 + this.padding, 0],
      [bbox.width + 2 * this.padding, bbox.height + 2 * this.padding],
    ];
    tri.setAttribute('points', points.map(point => point.join(',')).join(' '));
    return tri;
  }
}

