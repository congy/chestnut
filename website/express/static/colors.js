const COLORS_LEN = 16;
const COLORS = new Array(COLORS_LEN).fill().map((_, i) => {
  const a = Math.PI * 10;
  console.log((a * i) % 360);
  const rgb = hsluv.hsluvToRgb([ (a * i) % 360, 80, 90 ]);
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
