class VisualizerController {
    constructor(svg) {
        this.svg = svg;
    }
    async load() {
        const res = await fetch('/data');
        this.data = await res.json();
    }
    draw() {
        const svg = this.svg;
        const data = this.data;

        // Remove anything existing.
        while (svg.firstChild) {
            svg.removeChild(svg.firstChild);
        }

        // Build tables.
        const allTableVis = this.allTableVis = {};
        for (const [ table, { header, rows } ] of Object.entries(data)) {
            const idIndex = header.indexOf('id');
            const color = getColorFromTable(table);

            const allRecordVis = [];
            for (const row of rows) {
                const recordVis = new VisRecord(table.slice(0, 1).toUpperCase() + row[idIndex], color, { table, row });
                allRecordVis.push(recordVis);
            }

            const tableVis = new VisStack(allRecordVis);
            allTableVis[table] = tableVis;
        }

        // Table of Contents.
        const toc = getColorTable();
        const tocItems = Object.entries(toc).map(([ tableName, color ]) => new VisRecord(`${tableName} (${tableName.slice(0, 1).toUpperCase()})`, color));
        const tocVis = new VisStack([ new VisElem(createTextEl('Tables (On Disk)')), ...tocItems ], true, 20);
        const tocBox = new VisBox(tocVis, 'rgba(0, 0, 0, 0.05)', 20);

        const diskVis = new VisStack([ new VisElem(createTextEl('Records')), ...Object.values(allTableVis) ], true, 20);
        const diskBox = new VisBox(diskVis, 'rgba(0, 0, 0, 0.05)', 20); // TODO find out color order.

        const tocDiskVis = new VisStack([ tocBox, diskBox ], false, -1);

        const chestnutVis = new VisStack([ new VisElem(createTextEl('Chestnut (In-Memory)')) ], true, 20);
        const chestnutBox = new VisBox(chestnutVis, 'rgba(0, 0, 0, 0.05)', 20); // TODO find out color order.
        this.chestnutVis = chestnutVis;

        const root = new VisStack([ tocDiskVis, chestnutBox ], true, 20);
        root.attach(svg, 0, 0);
    }
    async play() {
        const chestnutModel = new ChestnutModel(JSON_MODEL, this.data);
        chestnutModel.bind(this.svg, this.allTableVis);
        await chestnutModel.form(this.svg, this.chestnutVis, () => delay(75));
    }
}
