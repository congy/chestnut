const COLORS_LEN = 16;
const COLORS = new Array(COLORS_LEN).fill().map((_, i) => {
  const rgb = hsluv.hsluvToRgb([ 70 * i % 360, 80, 90 ]);
  return '#' + rgb.map(x => (x * 255)|0)
    .map(x => x.toString(16).padStart(2, '0'))
    .join('');
});

const getColorFromTable = (() => {
  const colorTable = {};
  let i = 0;
  return function(tableName) {
    return colorTable[tableName] = colorTable[tableName] || COLORS[i++ % COLORS_LEN];
  };
})();
