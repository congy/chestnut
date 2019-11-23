
const delay = (d) => new Promise(resolve => setTimeout(resolve, d));
//const frame = () => new Promise(resolve => window.requestAnimationFrame(resolve));
//const delayFrame = (d) => Promise.all([ delay(d), frame() ]).then(() => {});


function moveEl(el, x, y) {
    if (typeof x !== 'number' || typeof y !== 'number')
        throw Error('x, y must be numeric.');
    //el.setAttribute('transform', `translate(${x}, ${y})`);
    el.setAttribute('style', `transform: translate(${x}px, ${y}px)`);
}

function createGroupEl() {
    const el = document.createElementNS(xmlns, "g");
    return el;
}

function createTextEl(text) {
    const el = document.createElementNS(xmlns, "text");
    el.textContent = text;
    el.setAttribute('dominant-baseline', 'text-before-edge');
    return el;
}

function createRectEl() {
    const el = document.createElementNS(xmlns, "rect");
    el.setAttribute('fill', 'white');
    el.setAttribute('stroke', 'black');
    return el;
}

class Vis {
    constructor() {
        this.parent = null;
    }
    setParent(parent) {
        if (null === parent)
            throw Error('set parent null.');
        this.parent = parent;
    }
    reflowParent() {
        // console.log(`reflow ${this.constructor.name} -> parent ${this.parent && this.parent.constructor.name}`);
        if (null !== this.parent)
            this.parent.reflow(this);
    }
}

class VisElem extends Vis {
    constructor(elem) {
        super();
        this.elem = elem;
    }
    reflow(child) {
        this.reflowParent();
    }
    move(x, y) {
        moveEl(this.elem, x, y);
    }
    size() {
        if (!this.elem.parentNode)
            throw Error('Cannot call size() before attach()');
        return this.elem.getBBox();
    }
    attach(svg, x, y) {
        this.move(x, y);
        svg.appendChild(this.elem);
    }
    clone(svg) {
        const copy = new VisElem(elem.cloneNode(true));
        copy.attach(svg, this.x, this.y);
        return copy;
    }
}

class VisBox extends Vis {
    constructor(item, color = 'white', pad = 0) {
        super();

        this.item = item;
        this.item.setParent(this);

        this.color = color;
        this.rect = createRectEl();
        this.rect.setAttribute('fill', color);

        this.pad = pad;
        this.width = 0;
        this.height = 0;

        this.x = null;
        this.y = null;
    }
    _update() {
        let { width, height } = this.item.size();
        width  += 2 * this.pad;
        height += 2 * this.pad;

        if (this.width === width && this.height === height)
            return false;

        this.rect.setAttribute('width',  width);
        this.rect.setAttribute('height', height);

        this.width  = width;
        this.height = height;

        return true;
    }
    reflow(child) {
        if (this._update())
            this.reflowParent();
    }
    move(x, y) {
        if (this.x === x && this.y === y)
            return;

        this.x = x;
        this.y = y;

        this.item.move(x + this.pad, y + this.pad);
        moveEl(this.rect, x, y);
    }
    size() {
        return { width: this.width, height: this.height };
    }
    attach(svg, x, y) {
        this.x = x;
        this.y = y;

        moveEl(this.rect, x, y);
        svg.appendChild(this.rect);
        this.item.attach(svg, x + this.pad, y + this.pad);

        this._update();
    }
    clone(svg) {
        throw new Error('not implemented.');
        const copy = new VisBox(this.item.clone(svg), this.color, this.pad);
        copy.attach(svg, this.x, this.y);
        return copy;
    }
}

const vrPad = 5;
const vrSpacing = 5;
class VisRecord extends Vis {

    constructor(id, color = 'rgba(255, 0, 0, 0.1)', data = null) {
        super();
        this.id = id;
        this.data = data;

        this.text = createTextEl(`id=${id}`);
        // this.box = createRectEl();
        // this.box.setAttribute('fill', color);

        this.stack = new VisStack([ new VisElem(this.text) ], true, vrSpacing);
        // this.stack.setParent(this);

        this.color = color;
        this.box = new VisBox(this.stack, color, vrPad);
        this.box.setParent(this);

        this.width = 0;
        this.height = 0;

        this.x = null;
        this.y = null;
    }
    reflow(child) {
        let { width, height } = this.box.size();

        if (this.width === width && this.height === height)
            return;

        // this.box.setAttribute('width',  nw);
        // this.box.setAttribute('height', nh);

        this.width  = width;
        this.height = height;

        this.reflowParent();
    }
    move(x, y) {
        if (this.x === x && this.y === y)
            return;

        this.x = x;
        this.y = y;
        // moveEl(this.text, x + VisRecord.pad, y + VisRecord.pad);
        // this.stack.move(x + VisRecord.pad, y + VisRecord.pad);
        // moveEl(this.box, x, y);
        this.box.move(x, y);
    }
    size() {
        return { width: this.width, height: this.height };
    }
    attach(svg, x, y) {
        this.x = x;
        this.y = y;

        this.box.attach(svg, x, y);
        const { width, height } = this.box.size();

        this.width = width;
        this.height = height;
    }
    clone(svg) {
        const copy = new VisRecord(this.id, this.color, JSON.parse(JSON.stringify(this.data)));
        copy.attach(svg, this.x, this.y);
        return copy;
    }

    // Add sub-DS.
    push(item) {
        this.stack.push(item);
    }
}

class VisStack extends Vis {
    constructor(items = [], isVert = false, pad = 0) {
        super();

        this.items = items;
        this.items.forEach(item => item.setParent(this));

        this.pad = pad;
        this.width = 0;
        this.height = 0;
        this.isVert = isVert;

        this.x = null;
        this.y = null;
    }
    _update(triggerIndex = -1, attachSvg = null) {
        let x = this.x;
        let y = this.y;

        let w = 0;
        let h = 0;

        if (this.items.length) {
            for (let i = 0; i < this.items.length; i++) {
                const item = this.items[i];
                if (attachSvg)
                    item.attach(attachSvg, x, y);
                else if (i > triggerIndex)
                    item.move(x, y);
                const { width, height } = item.size();

                if (this.isVert) {
                    w = Math.max(w, width);
                    h += height + this.pad;
                    y += height + this.pad;
                }
                else {
                    h = Math.max(h, height);
                    w += width + this.pad;
                    x += width + this.pad;
                }
            }

            if (this.isVert) {
                h -= this.pad;
                y -= this.pad;
            }
            else {
                w -= this.pad;
                x -= this.pad;
            }
        }

        if (this.width === w && this.height === h)
            return false;

        this.width = w;
        this.height = h;
        return true;
    }
    reflow(child) {
        if (this._update(this.items.indexOf(child)))
            this.reflowParent(this);
    }
    move(x, y, attachSvg = null) {
        if (this.x === x && this.y === y)
            return;

        this.x = x;
        this.y = y;

        this._update(-1, attachSvg);
    }
    size() {
        return { width: this.width, height: this.height };
    }
    attach(svg, x, y) {
        this.move(x, y, svg);
    }
    clone(svg) {
        throw Error('no clone visstack yet :(');
    }

    length() {
        return this.items.length;
    }
    push(item) {
        this.items.push(item);
        item.setParent(this);

        this.reflow(); // TODO could make this more efficient (?).
    }
    get(i) {
        return this.items[i];
    }
}
