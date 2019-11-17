
const delay = (d) => new Promise(resolve => setTimeout(resolve, d));
const frame = () => new Promise(resolve => window.requestAnimationFrame(resolve));
const delayFrame = (d) => Promise.all([ delay(d), frame() ]).then(() => {});

async function main() {
    const svg = document.getElementsByTagName('svg')[0];
    const visArray = new VisStack();

    const outs = new Array(10).fill()
        .map(() => new VisStack([], true));
    // outs.forEach((v, i) => v.move(60 * i, 35));
    const outStack = new VisStack(outs);
    outStack.attach(svg);
    outStack.move(0, 60);

    const visItems = new Array(20).fill()
        .map((_, i) => new VisRecord(81 + i));
    visItems.forEach(visItem => {
        //visItem.show();
        visItem.attach(svg)
    });

    for (const visItem of visItems) {
        visItem.attach(svg);
        await delay(100);
        visArray.push(visItem);
    }

    await delay(800);

    for (let j = 0; j < outs.length * 30; j++) {
        const i = (Math.random() * visArray.length()) | 0;
        const item = visArray.get(i).clone();
        item.attach(svg);

        await delay(5);
        delay(50).then(() => {
            window.requestAnimationFrame(() => {
                const a = outs[(Math.random() * outs.length) | 0];
                //debugger;
                a.push(item);
                //a.move(a.x - 10 * Math.random() - 15, a.y);

                if (Math.random() < 0.1) {
                    const x = a.get((Math.random() * a.length() / 2) | 0);

                    const bb = new VisElem(createTextEl("hi"));
                    bb.attach(svg)
                    x.box.item.push(bb);
                }
            });
        });
    }
}

function moveEl(el, x, y) {
    if (typeof x !== 'number' || typeof y !== 'number')
        throw Error('x, y must be numeric.');
    el.setAttribute('transform', `translate(${x}, ${y})`);
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
    attach(svg) {
        svg.insertBefore(this.elem, svg.firstChild);
    }
    clone() {
        return new VisElem(elem.cloneNode(true));
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
    attach(svg) {
        this.item.attach(svg);
        this.item.move(this.pad, this.pad);
        svg.insertBefore(this.rect, svg.firstChild);
        this._update();
    }
    clone() {
        return new VisBox(this.item.cloneNode(), this.color, this.pad);
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

        const stack = new VisStack([ new VisElem(this.text) ], true, vrSpacing);
        // this.stack.setParent(this);

        this.box = new VisBox(stack, color, vrPad);
        this.box.setParent(this);

        this.width = 0;
        this.height = 0;

        this.x = null;
        this.y = null;
    }
    reflow(child) {
        let { width, height } = this.box.size();

        if (this.width === width && this.height === height) {
            return;
        }

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
    attach(svg) {
        // // svg.attach(this.text);
        // let { width, height } = this.text.getBBox();

        // width  += 2 * VisRecord.pad;
        // height += 2 * VisRecord.pad;

        // this.box.setAttribute('width', width);
        // this.box.setAttribute('height', height);
        // // svg.attach(this.box);

        this.box.attach(svg);
        const { width, height } = this.box.size();

        this.width = width;
        this.height = height;
    }
    clone() {
        const clone = new VisRecord(this.id);
        clone.move(this.x, this.y);
        return clone;
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
    _update(triggerIndex = -1) {
        let x = this.x || 0;
        let y = this.y || 0;

        let w = 0;
        let h = 0;

        if (this.items.length) {
            for (let i = 0; i < this.items.length; i++) {
                const item = this.items[i];
                if (i > triggerIndex)
                    item.move(x, y);
                const { width, height} = item.size();
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
    move(x, y) {
        if (this.x === x && this.y === y)
            return;

        this.x = x;
        this.y = y;
        this._update();
    }
    size() {
        return { width: this.width, height: this.height };
    }
    attach(svg) {
        this.items.forEach(item => item.attach(svg));
        this._update();
    }
    clone() {
        throw Error('no clone visarray yet :(');
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
