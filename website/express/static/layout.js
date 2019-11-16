class StackLayout {
  constructor(items, pad, isVert) {
    this.items = items;
    this.pad = pad;
    this.isVert = isVert;
  }
  draw(svg, pos) {
    checkArgs(svg, pos);

    if (0 == this.items.length)
      return { w: 0, h: 0 };

    let { x, y } = pos;
    let b = 0;

    for (const item of this.items) {
      const { w: wi, h: hi } = item.draw(svg, { x, y });
      console.log({ wi, hi });

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

    console.log(this.isVert, x, pos.x);
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
  draw(svg, { x, y }) {
    checkArgs(svg, { x, y });

    let { w, h } = this.item.draw(svg, { x: x + this.pad, y: y + this.pad });

    console.log(w, h);
    if (w == 0 || h == 0)
      console.log(this.item);

    w += 2 * this.pad;
    h += 2 * this.pad;

    const box = document.createElementNS(xmlns, "rect");
    svg.prepend(box);
    box.setAttribute('fill', 'white');
    box.setAttribute('stroke', 'black');
    box.setAttribute('x', x);
    box.setAttribute('y', y);
    box.setAttribute('width', w);
    box.setAttribute('height', h);

    for (const kv of Object.entries(this.attr))
      box.setAttribute(...kv);

    return passCheckWH({ w, h });
  }
}

class Text {
  constructor(text) {
    this.text = text;
  }
  draw(svg, { x, y }) {
    checkArgs(svg, { x, y });

    const el = document.createElementNS(xmlns, "text");
    svg.prepend(el);
    el.textContent = this.text;
    el.setAttribute('dominant-baseline', 'text-before-edge');
    el.setAttribute('x', x);
    el.setAttribute('y', y);

    console.log(el.getBBox(), bboxToWH(el.getBBox()));

    return passCheckWH(bboxToWH(el.getBBox()));
  }
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