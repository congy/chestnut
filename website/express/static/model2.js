class ChestnutModel {
    constructor(model, data) {
        // Top level data structures.
        this.tlds = Object.values(model).map(x => {
            const table = getTableFromPath(x.table);
            const { header, rows } = data[table];
            return getDS(x, data, rows);
        });
    }
    // Clone items. ("bind" to existing.)
    bind(svg, allTableVis) {
        this.tlds.map(ds => ds.bind(svg, allTableVis));
    }
    // Form items into new DS.
    async form(svg, chestnutVis, delayFn) {
        for (const ds of this.tlds) {
            await delayFn();
            await ds.form(svg, chestnutVis, delayFn);
        }
    }
}

function getDS(model, data, rows, parentTableName = null) {
    if ('Index' === model.type) return new IndexDS(model, data, rows, parentTableName);
    if ('BasicArray' === model.type) return new ArrayDS(model, data, rows, parentTableName);
    throw new Error(`Unknown type: '${model.type}'`);
}

class DS {
    constructor(model, data, rows, parentTableName = null) {
        if (!Array.isArray(rows))
            throw Error(`ROWS NOT ARRAY: ${rows}.`);

        this.type = model.type;
        this.path = model.table;
        this.value = model.value;

        this.table = determineTableName(data, model, parentTableName);

        this.color = getColorFromTable(this.table);

        this.condition = model.condition;

        let { header, rows: allRows } = data[this.table];
        this.rows = getRowSubsetByCondition({ header, rows }, model.condition);

        console.log(`${this.type}[${this.path}]: ${this.rows.length}/${data[this.table].rows.length} rows.`);

        this.records = this.rows.map(row => new Record(model, data, row, parentTableName));
    }
    bind(svg, allTableVis) {
        this.records.map(record => record.bind(svg, allTableVis));
    }
    async form(svg, chestnutVis, delayFn) {
        const dsVis = new VisStack();
        //dsVis.attach(svg, 0, 0); // Doesn't really matter where it is attached.
        chestnutVis.push(dsVis);

        for (const record of this.records) {
            await delayFn();
            await record.form(svg, dsVis, delayFn);
        }
    }
}
class ArrayDS extends DS {
  // constructor(model, data, rows) {
  //   super(model, data, rows);
  // }
}
class IndexDS extends DS {
  // constructor(model, data, rows) {
  //   super(model, data, rows);
  // }
}


class Record {
    constructor(model, data, row, parentTableName = null) {
        this.row = row;
        this.path = model.table;

        this.table = determineTableName(data, model, parentTableName);

        const { header, rows: allRows } = data[this.table];

        this.recordId = row[header.indexOf('id')] - 1;
        if (this.recordId < 0) throw new Error(`Bad recordId: ${this.recordId}.`);

        this.nested = (model.value && model.value.nested || [])
            .map(nestedModel => {
                const nestedRows = getNestedRows(data, model, header, row, nestedModel);
                return getDS(nestedModel, data, nestedRows, this.table);
            });
    }
    bind(svg, allTableVis) {
        const tableVis = allTableVis[this.table];
        if (!tableVis) throw Error(`Failed to find table "${this.table}" from tables ${Object.keys(allTableVis)}.`);
        const recordVisToClone = tableVis.get(this.recordId);
        if (!recordVisToClone) return; // SHIELD.

        this._recordVis = recordVisToClone.clone(svg);

        this.nested.forEach(nest => nest.bind(svg, allTableVis));
    }
    async form(svg, dsVis, delayFn) {
        if (!this._recordVis) return; // SHIELD.

        dsVis.push(this._recordVis);

        for (const nest of this.nested) {
            await delayFn();
            await nest.form(svg, this._recordVis, delayFn);
        }
    }
}



async function main() {
    const svg = document.getElementsByTagName('svg')[0];
    const res = await fetch('/data');
    const data = await res.json();

    const allTableVis = {};
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
    const tocVis = new VisStack([ new VisElem(createTextEl('Tables')), ...tocItems ], true, 20);
    const tocBox = new VisBox(tocVis, 'none', 25);

    const diskVis = new VisStack([ new VisElem(createTextEl('Records')), ...Object.values(allTableVis) ], true, 20);
    const diskBox = new VisBox(diskVis, 'none', 25); // TODO find out color order.

    const tocDiskVis = new VisStack([ tocBox, diskBox ], false, -1);

    const chestnutVis = new VisStack([ new VisElem(createTextEl('Chestnut (In-Memory)')) ], true, 20);
    const chestnutBox = new VisBox(chestnutVis, 'none', 25); // TODO find out color order.

    const root = new VisStack([ tocDiskVis, chestnutBox ], true, 25);
    root.attach(svg, 0, 0);

    await delay(100);

    const chestnutModel = new ChestnutModel(JSON_MODEL, data);
    chestnutModel.bind(svg, allTableVis);
    await chestnutModel.form(svg, chestnutVis, () => delay(20));
}
