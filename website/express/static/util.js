function getTableFromPath(path) {
  return path.split('.').pop();
}
const OP_FNS = {
  '<':  (l, r) => l <  r,
  '<=': (l, r) => l <= r,
  '=':  (l, r) => l == r,
  '>=': (l, r) => l >= r,
  '>':  (l, r) => l >  r,
};
function getRowSubsetByCondition([ header, rows ], conditionString=null) {
  if (!conditionString)
    return rows;

  let [ lname, op, rname ] = parseCondition(conditionString);

  // Index of column we care about.
  let i = header.indexOf(lname);

  if (i < 0)
    throw Error(`Unknown col: "${lname}".`);

  if (rname.indexOf('param') === 0)
    return rows;


  throw Error(`Don't know how to handle: "${rname}".`);

  let opFn = OP_FNS[op];

  if (!opFn)
    throw Error(`Unknown op: "${op}".`);

  // Just return the rows matching the condition...
  // Choose the middle value as the right hand side. (TODO?).
  let values = rows.map(row => row[i]);
  values.sort(); // LEXICOGRAPHICAL ORDERING OF NUBMERS (TODO?).

  let rhs = values[values.length / 2];

  return rows.filter(row => opFn(row[i], rhs));
}

function parseCondition(conditionString) {
  const match = /(\S+)\s+(<|<=|=|>=|>)\s+(\S+)/g.exec(conditionString);
  if (!match)
    throw new Error(`Failed to match conditionString: "${conditionString}".`);
  return match.slice(1);
}

function getNestedRows(data, model, header, row, nestedModel) {
  const tableName = getTableFromPath(model.table);
  const nestedName = getTableFromPath(nestedModel.table);

  // slice is HACK for plurality.
  const { header: nestedHeader, rows: nestedAllRows } = data[nestedName] || data[nestedName.slice(0, -1)];

  const keyManyToOne = nestedName + '_id';
  const keyOneToMany = tableName + '_id';

  if (header.includes(keyManyToOne)) {
    const i = header.indexOf(keyManyToOne);
    const j = nestedHeader.indexOf('id');

    if (i < 0 || j < 0)
      throw Error(`Failed to determine join column, this table header: ${header}, sub-table: ${nestedModel.table}, i: ${i}, j: ${j}.`);

    const nestedRows = nestedAllRows.filter(nestedRow => row[i] == nestedRow[j]);
    return nestedRows;
  }
  else if (nestedHeader.includes(keyOneToMany)) {
    const i = header.indexOf('id');
    const j = nestedHeader.indexOf('id');

    // TODO fix duplicate code.
    if (i < 0 || j < 0)
      throw Error(`Failed to determine join column, this table header: ${header}, sub-table: ${nestedModel.table}, i: ${i}, j: ${j}.`);

    const nestedRows = nestedAllRows.filter(nestedRow => row[i] == nestedRow[j]);
   return nestedRows;
  }
  // Many to Many
  else {
    let manyTable = tableName + '_' + nestedName;
    console.log(manyTable);
    //throw Error(`Failed to join: ${tableName}: ${header}, nested ${nestedName}: ${nestedHeader}.`);
  }
}




function promiseDelay(delay) {
  return new Promise(resolve => window.setTimeout(resolve, delay));
}