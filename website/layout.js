class StackLayout {
  constructor(items, padding, isVert) {
    this.items = items;
    this.padding = padding;
    this.isVert = isVert;
  }
  draw(svg) {
    const group = document.createElementNS(xmlns, "g");
    svg.appendChild(group);

    let b = 0;
    for (const item of this.items) {
      const el = item.draw(svg);
      // Check EL.
      if (!(el instanceof Node)) {
        console.log(item);
        throw new Error(`Item's draw() failed to return node.`);
      }
      group.appendChild(el);

      const bbox = el.getBBox();

      el.setAttribute('transform', this.isVert
        ? `translate(0, ${b})`
        : `translate(${b}, 0)`);

      b += bbox[this.isVert ? 'height' : 'width'] + this.padding;
    }
    return group;
  }
}

class VStackLayout extends StackLayout {
  constructor(items, padding) {
    super(items, padding, true);
  }
}
class HStackLayout extends StackLayout {
  constructor(items, padding) {
    super(items, padding, false);
  }
}
