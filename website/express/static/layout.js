class StackLayout {
  constructor(items, pad, isVert) {
    this.items = items;
    this.pad = pad;
    this.isVert = isVert;
  }
  draw(svg, pos, meta) {
    checkArgs(svg, pos);

    if (0 == this.items.length)
      return { w: 0, h: 0 };

    let { x, y } = pos;
    let b = 0;

    for (const item of this.items) {
      const { w: wi, h: hi } = item.draw(svg, { x, y }, meta);

      if (this.isVert) {
        y += hi + this.pad;
        b = Math.max(b, wi);
      }
      else {
        x += wi + this.pad;
        b = Math.max(b, hi);
      }
    }

    // Remove trailing pad.
    y -= this.pad;
    x -= this.pad;

    return passCheckWH(this.isVert
      ? { w: b, h: y - pos.y }
      : { w: x - pos.x, h: b });
  }
}
class VStackLayout extends StackLayout {
  constructor(items, pad) {
    super(items, pad, true);
  }
}
class HStackLayout extends StackLayout {
  constructor(items, pad) {
    super(items, pad, false);
  }
}

class Box {
  constructor(item, pad, attr = {}) {
    this.item = item;
    this.pad = pad;
    this.attr = attr;
  }
  draw(svg, { x, y }, meta) {
    checkArgs(svg, { x, y });

    let { w, h } = this.item.draw(svg, { x: x + this.pad, y: y + this.pad }, meta);

    if (w == 0 || h == 0)
      console.log(this.item);

    w += 2 * this.pad;
    h += 2 * this.pad;

    const box = createBox(x, y, w, h, this.attr);
    svg.prepend(box);

    return passCheckWH({ w, h });
  }
}

function createBox(x, y, width, height, attr = {}) {
  const box = document.createElementNS(xmlns, "rect");
  box.setAttribute('fill', 'white');
  box.setAttribute('stroke', 'black');
  box.setAttribute('transform', `translate(${x}, ${y})`);
  box.setAttribute('width', width);
  box.setAttribute('height', height);
  for (const kv of Object.entries(attr))
    box.setAttribute(...kv);
  return box;
}

class Text {
  constructor(text) {
    this.text = text;
  }
  draw(svg, { x, y }, meta) {
    checkArgs(svg, { x, y });

    const el = createText(this.text, x, y);
    svg.prepend(el);

    return passCheckWH(bboxToWH(el.getBBox()));
  }
}

function createText(text, x, y) {
  const el = document.createElementNS(xmlns, "text");
  el.textContent = text;
  el.setAttribute('dominant-baseline', 'text-before-edge');
  el.setAttribute('transform', `translate(${x}, ${y})`);
  return el;
}

function checkArgs(svg, pos) {
  if (!svg) throw Error('SVG missing.');
  if (!pos) throw Error('POS missing.');
  if (typeof pos.x !== 'number') throw Error('POS.X not number.');
  if (typeof pos.y !== 'number') throw Error('POX.Y not number.');
}
function passCheckWH({ w, h }) {
  if (w < 0) throw Error('W negative.');
  if (h < 0) throw Error('H negative.');
  return { w, h };
}
function bboxToWH(bbox) {
  return { w: bbox.width, h: bbox.height };
}