function getTableFromPath(path) {
  if (!path) throw Error('Cannot get table from missing path: ' + path);
  return path[path.length - 1];
}
const OP_FNS = {
  '<':  (l, r) => l <  r,
  '<=': (l, r) => l <= r,
  '==': (l, r) => l == r,
  '>=': (l, r) => l >= r,
  '>':  (l, r) => l >  r,
};
function getRowSubsetByCondition({ header, rows }, conditionString=null) {
  if (!rows.every(row => Array.isArray(row)))
    throw Error(`rows must be array of arrays.`);


  if (!conditionString)
    return rows;

  let [ lname, op, rname ] = parseCondition(conditionString);

  console.log(lname, op, rname);

  // Index of column we care about.
  let i = header.indexOf(lname);

  if (i < 0)
    throw Error(`Unknown col: "${lname}".`);

  if (rname.indexOf('param') === 0) // TODO hack.
    return rows;


  //throw Error(`Don't know how to handle: "${rname}".`);

  let opFn = OP_FNS[op];
  if (!opFn)
    throw Error(`Unknown op: "${op}".`);

  if (rname.startsWith("'") || rname.startsWith('"')) {
    const rval = eval(rname); // EVAL.
    console.log(rval, rows);
    return rows.filter(row => opFn(row[i], rval));
  }

  // Just return the rows matching the condition...
  // Choose the middle value as the right hand side. (TODO?).
  let values = rows.map(row => row[i]);
  values.sort(); // LEXICOGRAPHICAL ORDERING OF NUBMERS (TODO?).

  let rhs = values[values.length / 2];

  return rows.filter(row => opFn(row[i], rhs));
}

function parseCondition(conditionString) {
  const match = /(\S+)\s+(<|<=|==|>=|>)\s+(\S+)/g.exec(conditionString);
  if (!match)
    throw new Error(`Failed to match conditionString: "${conditionString}".`);
  return match.slice(1);
}

function getRowById(header, rows, id) {
  const i = header.indexOf('id');
  return rows.find(row => id === row[i]);
}

function determineTableName(data, model, parentTableName = null) {
  const assoc = model.association;

  if (parentTableName && assoc) {
    if (!data[parentTableName]) throw Error(
      `Cannot find child table when parent table with name ${parentTableName} doesn't exist.`);
    if (assoc.leftTable === parentTableName)
      return assoc.rightTable;
    if (assoc.rightTable === parentTableName)
      return assoc.leftTable;
    throw Error(`Failed to determine name for nested table: ${model.table}, parent: ${parentTableName}`);
  }
  else {
    let name = getTableFromPath(model.table);
    if (!data[name]) name = name.slice(0, -1);
    if (!data[name]) throw Error(`Failed to determine name for table: ${model.table}`);
    return name;
  }
}

function getNestedRows(data, model, header, row, nestedModel) {
  let tableName = getTableFromPath(model.table);
  if (!data[tableName]) tableName = tableName.slice(0, -1);
  if (!data[tableName]) throw Error(`failed to find table: ${tableName}`);
  const nestedName = getTableFromPath(nestedModel.table);

  // const keyManyToOne = nestedName + '_id';
  // const keyOneToMany = tableName + '_id';

  const assoc = nestedModel.association;

  if (assoc) {
    let parentIsLeft;
    if (assoc.leftTable === tableName) {
      //console.log('left table is parent table.');
      parentIsLeft = true;
    }
    else if (assoc.rightTable === tableName) {
      //console.log('right table is parent table.');
      parentIsLeft = true;
    }
    else {
      throw Error(`Association without either table?`);
    }

    const { header: nestedHeader, rows: nestedAllRows } = data[parentIsLeft ? assoc.rightTable : assoc.leftTable];

    if ('many_to_many' === assoc.assocType) {
      const { header: assocHeader, rows: assocRows } = data[assoc.table];
      const tableIdIndex = header.indexOf('id');
      const rowId = row[tableIdIndex];

      // TODO this may need to be left-right indifferent.
      const assocTableFkIndex = assocHeader.indexOf(parentIsLeft ? assoc.leftFkField : assoc.rightFkField);
      const assocNestedFkIndex = assocHeader.indexOf(parentIsLeft ? assoc.rightFkField : assoc.leftFkField);

      const nestedRows = [];
      for (const assocRow of assocRows) {
        const assocTableFk = assocRow[assocTableFkIndex];
        const assocNestedFk = assocRow[assocNestedFkIndex];
        if (rowId === assocTableFk) {
          nestedRows.push(getRowById(nestedHeader, nestedAllRows, assocNestedFk));
        }
      }
      // if (!nestedRows.length) debugger;
      return nestedRows;
    }
    else {
      // console.log(assoc);

      const parentTableKeyField = parentIsLeft ? 'id' : assoc.rightFkField;
      const parentTableKeyIndex = header.indexOf(parentTableKeyField);
      if (parentTableKeyIndex < 0) throw Error(`Failed to find field "${parentTableKeyField}" in table "${tableName}", header: ${header}`);

      const nestedTableKeyField = parentIsLeft ? assoc.rightFkField : 'id';
      const nestedTableKeyIndex = nestedHeader.indexOf(nestedTableKeyField);
      if (nestedTableKeyIndex < 0) throw Error(`Failed to find field "${nestedTableKeyField}" in table "${nestedName}", header: ${nestedHeader}`);

      const key = row[parentTableKeyIndex];

      const nestedRows = [];
      for (const nestedRow of nestedAllRows) {
        if (key === nestedRow[nestedTableKeyIndex]) {
          nestedRows.push(nestedRow);
        }
      }
      // if (!nestedRows.length) debugger;
      return nestedRows;
    }
  }

  // INDICES FROM HERE ON?

  // slice is HACK for trailing 's'.
  const { header: nestedHeader, rows: nestedAllRows } = data[nestedName] || data[nestedName.slice(0, -1)];

  // TODO clean up this code to use the `assoc`.

  /*if (header.includes(keyManyToOne)) {
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
    //let manyTable = tableName + '_' + nestedName;
    //console.log(manyTable);
  }*/
  console.log('!TODO!', nestedModel.association);
  return nestedAllRows;
  throw Error(`Failed to join: ${tableName}: ${header}, nested ${nestedName}: ${nestedHeader}.`);
}
