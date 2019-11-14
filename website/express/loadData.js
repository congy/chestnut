const util = require('util');
const fs = require('fs');
fs.readdirAsync = util.promisify(fs.readdir);
fs.readFileAsync = util.promisify(fs.readFile);

const EXT = ".tsv";

async function loadData(path) {
    const data = {};
    const fileNames = await fs.readdirAsync(path);
    const promises = fileNames
        .filter(fileName => fileName.endsWith(EXT))
        .map(async fileName => {
            const name = fileName.slice(0, -EXT.length);
            const fileContent = await fs.readFileAsync(`${path}/${fileName}`, 'utf8');
            const [ header, ...rows ] = fileContent.trim().split(/[\r\n]+/g)
                .map(line => line.trim().split('|'));
            data[name] = { header, rows };
        });
    await Promise.all(promises);
    return data;
}

module.exports = loadData;
