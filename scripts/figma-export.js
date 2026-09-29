// designer 전용 S3/S4 덤프. use_figma로 실행하고, 아래 두 줄만 바꾼다.
// 반환값을 그대로 runs/<slug>/s3-keyscreens.json 또는 s4-system.json에 저장한다. 손으로 고치지 않는다.
const SLUG = "__SLUG__";
const MODE = "S3"; // "S3" | "S4"

const to255 = x => Math.round(x * 255);
const color = (c, a) => a >= 1
  ? "#" + [c.r, c.g, c.b].map(x => to255(x).toString(16).padStart(2, "0")).join("")
  : `rgba(${to255(c.r)},${to255(c.g)},${to255(c.b)},${+a.toFixed(2)})`;
const paints = ps => (!ps || ps === figma.mixed) ? []
  : ps.filter(p => p.type === "SOLID" && p.visible !== false).map(p => color(p.color, p.opacity ?? 1));
// ponytail: 텍스트 스타일이 섞인 노드는 "MIXED"로 내보내 판정에서 떨어진다. 필요하면 getStyledTextSegments로 세그먼트별 덤프.
const one = x => x === figma.mixed ? "MIXED" : x;

async function dump(n) {
  const o = { id: n.id, name: n.name, type: n.type, width: Math.round(n.width), height: Math.round(n.height) };
  if ("fills" in n) o.fills = paints(n.fills);
  if ("strokes" in n) o.strokes = paints(n.strokes);
  if ("cornerRadius" in n) o.radius = n.cornerRadius === figma.mixed
    ? Math.max(n.topLeftRadius, n.topRightRadius, n.bottomLeftRadius, n.bottomRightRadius) : n.cornerRadius;
  if ("effects" in n) o.effects = n.effects.filter(e => e.visible !== false).map(e => ({ type: e.type }));
  if ("layoutMode" in n && n.layoutMode !== "NONE") {
    o.padding = [n.paddingTop, n.paddingRight, n.paddingBottom, n.paddingLeft];
    o.itemSpacing = n.itemSpacing;
  }
  if (n.type === "INSTANCE") {
    const m = await n.getMainComponentAsync();
    o.component = m && (m.parent && m.parent.type === "COMPONENT_SET" ? m.parent.name : m.name);
  }
  if (n.type === "TEXT") {
    o.text = n.characters;
    o.fontFamily = n.fontName === figma.mixed ? "MIXED" : n.fontName.family;
    o.fontWeight = one(n.fontWeight);
    o.fontSize = one(n.fontSize);
    o.letterSpacing = n.letterSpacing === figma.mixed ? "MIXED" : n.letterSpacing.value;
  }
  const bv = n.boundVariables || {};
  o.bound = {
    fills: !!((bv.fills && bv.fills.length) || (bv.strokes && bv.strokes.length)),
    radius: !!(bv.topLeftRadius || bv.cornerRadius),
  };
  return o;
}

const page = figma.root.children.find(p => p.name === SLUG);
if (!page) throw new Error(`page not found: ${SLUG}`);
await page.loadAsync();

const frames = [];
for (const f of page.children.filter(c => c.type === "FRAME")) {
  const frame = await dump(f);
  frame.nodes = [];
  for (const n of f.findAll()) frame.nodes.push(await dump(n));
  frames.push(frame);
}

const out = { slug: SLUG, mode: MODE, frames };
if (MODE === "S4") {
  out.variables = (await figma.variables.getLocalVariablesAsync()).map(v => v.name);
  const sys = figma.root.children.find(p => p.name === "_system");
  if (sys) await sys.loadAsync();
  out.components = sys ? sys.findAllWithCriteria({ types: ["COMPONENT_SET", "COMPONENT"] }).map(c => c.name) : [];
}
return out;
