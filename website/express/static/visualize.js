
const delay = (d) => new Promise(resolve => setTimeout(resolve, d));
const frame = () => new Promise(resolve => window.requestAnimationFrame(resolve));
const delayFrame = (d) => Promise.all([ delay(d), frame() ]).then(() => {});

async function main() {
    const svg = document.getElementsByTagName('svg')[0];
    const visArray = new VisStack();

    const outs = new Array(10).fill()
        .map(() => new VisStack([], true));
    outs.forEach((v, i) => v.move(60 * i, 35));

    const visItems = new Array(20).fill()
        .map((_, i) => new VisRecord(i));
    visItems.forEach(visItem => {
        //visItem.show();
        visItem.prepend(svg)
    });

    for (const visItem of visItems) {
        visItem.prepend(svg);
        await delay(100);
        visArray.push(visItem);
    }

    await delay(800);

    for (let j = 0; j < outs.length * 30; j++) {
        const i = (Math.random() * visArray.length()) | 0;
        const item = visArray.get(i).clone();
        item.prepend(svg);

        await delay(5);
        delay(50).then(() => {
            window.requestAnimationFrame(() => {
                const a = outs[(Math.random() * outs.length) | 0];
                //debugger;
                a.push(item);
                //a.move(a.x - 10 * Math.random() - 15, a.y);

                if (Math.random() < 0.1) {
                    const x = a.get((Math.random() * a.length() / 2) | 0);

                    const bb = new VisElem(createTextEl("bb"));
                    bb.prepend(svg)
                    x.stack.push(bb);
                }
            });
        });
    }
}

function moveEl(el, x, y) {
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
    el.setAttribute('fill', 'rgba(255, 0, 0, 0.1)');
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
        return this.elem.getBBox();
    }
    prepend(svg) {
        svg.prepend(this.elem);
    }
    clone() {
        return new VisElem(elem.cloneNode(true));
    }
}

class VisRecord extends Vis {
    static pad = 5;
    static spacing = 5;

    constructor(id) {
        super();
        this.id = id;
        this.text = createTextEl(`id=${id}`);
        this.box = createRectEl();

        this.stack = new VisStack([ new VisElem(this.text) ], true);
        this.stack.setParent(this);
        this.move(0, 0);

        /* this.text.setAttribute('opacity', 0);
        this.box.setAttribute('opacity', 0); */
    }
    reflow(child) {
        const { width, height } = this.size();
        let { width: nw, height: nh } = this.stack.size();
        nw += 2 * VisRecord.pad;
        nh += 2 * VisRecord.pad;

        if (nw === width && nh === height) {
            return;
        }

        this.box.setAttribute('width',  nw);
        this.box.setAttribute('height', nh);

        this.reflowParent();
    }
    move(x, y) {
        this.x = x;
        this.y = y;
        // moveEl(this.text, x + VisRecord.pad, y + VisRecord.pad);
        this.stack.move(x + VisRecord.pad, y + VisRecord.pad);
        moveEl(this.box, x, y);
    }
    size() {
        return this.box.getBBox();
    }
    prepend(svg) {
        svg.prepend(this.text);
        const { width, height } = this.text.getBBox();
        this.box.setAttribute('width', width + 2 * VisRecord.pad);
        this.box.setAttribute('height', height + 2 * VisRecord.pad);
        svg.prepend(this.box);

        /* window.requestAnimationFrame(() => {
            this.text.setAttribute('opacity', 1);
            this.box.setAttribute('opacity', 1);
        }); */
    }
    clone() {
        const clone = new VisRecord(this.id);
        clone.move(this.x, this.y);
        return clone;
    }
}

class VisStack extends Vis {
    constructor(items = [], isVert = false) {
        super();

        this.items = items;
        this.items.forEach(item => item.setParent(this));

        this.width = 0;
        this.height = 0;
        this.isVert = isVert;

        this.move(0, 0);
    }
    _update(triggerIndex = -1) {
        let x = this.x;
        let y = this.y;

        let w = 0;
        let h = 0;

        for (let i = 0; i < this.items.length; i++) {
            const item = this.items[i];
            if (i > triggerIndex)
                item.move(x, y);
            const { width, height} = item.size();
            if (this.isVert) {
                w = Math.max(w, width);
                h += height;
                y += height;
            }
            else {
                h = Math.max(h, height);
                w += width;
                x += width;
            }
        }
        this.width = w;
        this.height = h;
    }
    reflow(child) {
        this._update();
        this.reflowParent(this.items.indexOf(child));
    }
    move(x, y) {
        this.x = x;
        this.y = y;
        this._update();
    }
    size() {
        return { width: this.width, height: this.height };
    }
    prepend(svg) {
        this.items.forEach(item => item.prepend(svg));
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
