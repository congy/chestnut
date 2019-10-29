function stackLayout(svg, elems, padding, isVert) {
  const group = document.createElementNS(xmlns, "g");
  svg.appendChild(group);

  let b = 0;
  for (const el of elems) {
    group.appendChild(el);

    const bbox = el.getBBox();

    el.setAttribute('transform', isVert
      ? `translate(0, ${b})`
      : `translate(${b}, 0)`);

    b += bbox[isVert ? 'height' : 'width'] + padding;
  }
  return group;
}

function vStackLayout(svg, items, padding = 0) {
  return stackLayout(svg, items, padding, true);
}
function hStackLayout(svg, items, padding = 0) {
  return stackLayout(svg, items, padding, false);
}

function drawTextElem(svg, text) {
  const el = document.createElementNS(xmlns, "text");
  el.textContent = text;
  el.setAttribute('dominant-baseline', 'text-before-edge');
  svg.appendChild(el);
  return el;
}

function drawBox(svg, childEl, padding = 0, attr = {}) {
  const group = document.createElementNS(xmlns, "g");
  svg.appendChild(group);

  group.appendChild(childEl);

  childEl.setAttribute('transform', `translate(${padding}, ${padding})`);

  const bbox = childEl.getBBox();

  const box = document.createElementNS(xmlns, "rect");
  box.setAttribute('fill', 'white');
  box.setAttribute('stroke', 'black');
  box.setAttribute('width', bbox.width + 2 * padding);
  box.setAttribute('height', bbox.height + 2 * padding);

  console.log(attr)
  for (const kv of Object.entries(attr))
    box.setAttribute(...kv);

  group.appendChild(box);
  group.appendChild(childEl);

  return group;
}