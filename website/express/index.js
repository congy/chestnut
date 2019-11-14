const express = require('express');
const exphbs  = require('express-handlebars');

const asyncHandler = require('express-async-handler');

const loadData = require('./loadData');

const CHESTNUT_DIR_NAME = 'chestnut';
const CHESTNUT_DIR = __dirname.slice(0, __dirname.indexOf(CHESTNUT_DIR_NAME) + CHESTNUT_DIR_NAME.length);

const hbs = exphbs.create({
    helpers: {
        section(name, options) {
            this.$sections = this.$sections || {};
            this.$sections[name] = options.fn(this);
            return null;
        }
    }
})

const app = express();
const port = 3000;

// Serve static files.
app.use('/static', express.static(__dirname + '/static'));

// Set up handlebars templates.
app.engine('handlebars', hbs.engine);
app.set('view engine', 'handlebars');

app.get('/', (req, res) => {
    res.render('home');
});
app.get('/data', asyncHandler(async (req, res) => {
    const data = await loadData(CHESTNUT_DIR + '/benchmark/kandan/data/kandan_diag');

    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(data, null, 2));
}));

app.listen(port, () => console.log(`Chestnut demo listening on port ${port}.`));
