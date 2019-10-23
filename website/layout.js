class VStackLayout {
    constructor(items) {
      this.items = items;
    }
    draw(svg) {
      for (let item of items) {
        item.draw(svg);
      }
    }
}


function helper_render_vstack(svg, elements, padding) {
  const group = document.createElementNS(xmlns, "g");
  svg.appendChild(group);

  const border = document.createElementNS(xmlns, "rect");
  group.appendChild(border);
  border.style.fill = 'none';

  let x = 0;
  let y = padding;
  for (const element of elements) {
    group.appendChild(element);
    element.setAttribute('transform', 'translate(' + padding + ',' + y + ')');

    const bbox = element.getBBox();
    console.log(bbox);
    x = Math.max(x, bbox.width);
    y += bbox.height + padding;
  }
  // Set border up.
  border.setAttribute('width', x + 2 * padding);
  border.setAttribute('height', y);

  return { group, border };
}
