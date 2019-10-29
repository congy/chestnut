
class NativeElement {
  constructor(el) {
    this.el = el;
  }
  draw(svg) {
    svg.appendChild(this.el);
    return this.el;
  }
}

class Spacer extends NativeElement {
  constructor(width, height) {
    const el = document.createElementNS(xmlns, "rect");
    el.setAttribute('fill', 'none');
    el.setAttribute('width', width);
    el.setAttribute('height', height);
    super(el);
  }
}

class TextElement extends NativeElement {
  constructor(text) {
    const el = document.createElementNS(xmlns, "text");
    el.textContent = text;
    el.setAttribute('dominant-baseline', 'text-before-edge');
    super(el);
  }
}
