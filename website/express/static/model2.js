function main() {
    const svg = document.getElementsByTagName('svg')[0];
    fetch('/data')
        .then(res => res.json())
        .then(async (data) => {

            const allTableVis = {};
            for (const [ table, { header, rows } ] of Object.entries(data)) {
                const idIndex = header.indexOf('id');
                const color = getColorFromTable(table);

                const allRecordVis = [];
                for (const row of rows) {
                    const recordVis = new VisRecord(row[idIndex], color, { table, row });
                    recordVis.attach(svg);
                    allRecordVis.push(recordVis);
                }

                const tableVis = new VisStack(allRecordVis);
                allTableVis[table] = tableVis;
            }

            const diskVis = new VisStack([ new VisElem(createTextEl('Disk')), ...Object.values(allTableVis) ], true, 20);
            const diskBox = new VisBox(diskVis, 'none', 25); // TODO find out color order.

            const chestnutVis = new VisStack([ new VisElem(createTextEl('Chestnut')) ], true, 20);
            const chestnutBox = new VisBox(chestnutVis, 'none', 25); // TODO find out color order.

            const root = new VisStack([ diskBox, chestnutBox ], true, 25);
            root.attach(svg);

            await delay(1000);

            // CHESTNUT SHIT.
            // for each top level data structure.
            for (const ds of Object.values(JSON_MODEL)) {
                const table = getTableFromPath(ds.table);

                const dsVis = new VisStack();
                dsVis.attach(svg);
                chestnutVis.push(dsVis);

                const { header, rows: allRows } = data[table];
                const idIndex = header.indexOf('id');
                const diskTableVis = allTableVis[table];

                const rows = getRowSubsetByCondition([ header, allRows ], ds.condition); // TODO does this
                for (let row of rows) {
                    const rowId = row[idIndex];

                    const recordVis = diskTableVis.get(rowId - 1).clone(); // TODO HACK.
                    recordVis.attach(svg);

                    delay(50).then(() => window.requestAnimationFrame(() => dsVis.push(recordVis)));
                    await delay(50);
                }
            }

            //const diag = new ChestnutModel(JSON_MODEL, data);
            //diag.draw(svg, { x: 100, y: 100 }, { state: 0 });
            //return promiseDelay(500);
        })
        //.then(() => {
        //  Record.moveAllToSavedPos();
        //});
}