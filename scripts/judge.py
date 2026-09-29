#!/usr/bin/env python3
"""하네스 판정자. 기준은 rules/rules.json 하나뿐.

사용법:
  python3 scripts/judge.py <slug> <G1|G2|S3|S4>   runs/<slug>/ 산출물 판정
  python3 scripts/judge.py --selftest             tests/fixtures + design.md 색 동기화 검사
출력: {"gate","pass","violations":[{"node","rule","value"}]} JSON. 통과 0, 실패 1로 종료.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "rules/rules.json").read_text())
FILES = {"G1": "s1-research.md", "G2": "s2-spec.md", "S3": "s3-keyscreens.json", "S4": "s4-system.json"}


def v(rule, value, node="-"):
    return {"node": node, "rule": rule, "value": value}


def norm(c):
    return c.lower().replace(" ", "")


COLORS = {norm(c) for c in R["colors"]}


def pii(text, where):
    return [v("rule_B", m.group(), where) for p in R["rule_B"]["pii_regex"] for m in re.finditer(p, text)]


def check_g1(text):
    out = []
    refs = re.split(r"^## ", text, flags=re.M)[1:]
    lo, hi = R["research"]["refs"]
    if not lo <= len(refs) <= hi:
        out.append(v("refs", len(refs)))
    for ref in refs:
        title = ref.splitlines()[0].strip()
        if not re.search(r"https?://(?:www\.)?uibowl\.io\S*", ref):
            out.append(v("uibowl_link", 0, title))
        points = re.findall(r"^- 반영:\s*\S", ref, re.M)
        if len(points) < R["research"]["min_points_per_ref"]:
            out.append(v("points", len(points), title))
    return out


def check_g2(text):
    out = []
    screens = re.split(r"^## 화면:", text, flags=re.M)[1:]
    lo, hi = R["spec"]["screens"]
    if not lo <= len(screens) <= hi:
        out.append(v("screens", len(screens)))
    a = R["rule_A"]
    for s in screens:
        name = s.splitlines()[0].strip()
        fields = dict(re.findall(r"^- ([^:\n]+):[ \t]*(.*)$", s, re.M))
        for f in R["spec"]["required_fields"]:
            if not fields.get(f, "").strip():
                out.append(v("required_field", f, name))
        if "판매 신청" in s and a["sale_request_role"] not in fields.get("권한", ""):
            out.append(v("rule_A", fields.get("권한", ""), name))
        for st in re.split(r"[,/]", fields.get("자산 상태", "")):
            if st.strip() and st.strip() not in a["asset_status"]:
                out.append(v("rule_A", st.strip(), name))
    for word in a["phase2_text"]:
        out += [v("rule_A", word)] * text.count(word)
    return out + pii(text, "s2-spec.md")


def radius_ok(n, r):
    w, h = n.get("width", 0), n.get("height", 0)
    if r in R["radius"] or (w and h and r >= min(w, h) / 2):  # 9999 대신 높이/2로 만든 pill도 허용
        return True
    is_icon = "app-icon-squircle" in f"{n.get('component', '')} {n.get('name', '')}"
    return is_icon and abs(r - R["radius_icon_ratio"] * w) <= 0.5


def check_frames(data, s4):
    out = []
    fr, font = R["frame"], R["font"]
    frames = data.get("frames", [])
    lo, hi = fr["count"]
    if not lo <= len(frames) <= hi:
        out.append(v("frame_count", len(frames)))
    for f in frames:
        if (f.get("width"), f.get("height")) != (fr["width"], fr["height"]):
            out.append(v("frame_size", f"{f.get('width')}x{f.get('height')}", f["id"]))
        accent = 0
        for n in [f] + f.get("nodes", []):
            nid, comp = n.get("id"), n.get("component")
            colors = n.get("fills", []) + n.get("strokes", [])
            for c in colors:
                if norm(c) not in COLORS:
                    out.append(v("color", c, nid))
            if norm(R["accent"]["value"]) in map(norm, colors):
                accent += 1
                if comp in R["accent"]["forbidden_on"]:
                    out.append(v("accent_on_cta", comp, nid))
            r = n.get("radius")
            if r is not None and not radius_ok(n, r):
                out.append(v("radius", r, nid))
            shadows = [e for e in n.get("effects", []) if "SHADOW" in e.get("type", "")]
            if len(shadows) > R["shadow"]["max"] and comp not in R["shadow"]["allow_components"]:
                out.append(v("shadow", len(shadows), nid))
            for sp in n.get("padding", []) + [n.get("itemSpacing", 0)]:
                if sp and sp not in R["spacing"]:
                    out.append(v("spacing", sp, nid))
            if n.get("type") == "TEXT":
                if not str(n.get("fontFamily", "")).startswith(font["family"]):
                    out.append(v("font_family", n.get("fontFamily"), nid))
                if n.get("fontWeight") not in font["weights"]:
                    out.append(v("font_weight", n.get("fontWeight"), nid))
                if n.get("fontSize") not in font["sizes"]:
                    out.append(v("font_size", n.get("fontSize"), nid))
                if n.get("letterSpacing") != font["letter_spacing"]:
                    out.append(v("letter_spacing", n.get("letterSpacing"), nid))
                out += pii(n.get("text", ""), nid)
            if s4:
                bound = n.get("bound", {})
                if colors and not bound.get("fills"):
                    out.append(v("unbound_color", colors, nid))
                if r and not bound.get("radius"):
                    out.append(v("unbound_radius", r, nid))
        if accent > R["accent"]["max_per_frame"]:
            out.append(v("accent_count", accent, f["id"]))
    if s4:
        for key in ("variables", "components"):
            if not data.get(key):
                out.append(v(f"no_{key}", 0))
    return out


def judge(gate, path):
    if not Path(path).exists():
        return {"gate": gate, "pass": False, "violations": [v("missing_file", str(path))]}
    text = Path(path).read_text()
    if gate == "G1":
        out = check_g1(text)
    elif gate == "G2":
        out = check_g2(text)
    else:
        out = check_frames(json.loads(text), s4=gate == "S4")
    return {"gate": gate, "pass": not out, "violations": out}


# 픽스처별로 반드시 잡혀야 하는 규칙. 엉뚱한 이유로 FAIL해도 셀프테스트가 걸러낸다.
EXPECT = {
    "G1-pass.md": set(), "G1-fail.md": {"refs"},
    "G2-pass.md": set(), "G2-fail-A.md": {"rule_A"}, "G2-fail-B.md": {"rule_B"},
    "S3-pass.json": set(), "S3-fail.json": {"radius", "shadow"},
    "S4-pass.json": set(), "S4-fail.json": {"unbound_color"},
}


def selftest():
    ok = True
    for name, want in EXPECT.items():
        res = judge(name.split("-")[0], ROOT / "tests/fixtures" / name)
        got = {x["rule"] for x in res["violations"]}
        good = res["pass"] if not want else want <= got
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}: pass={res['pass']} rules={sorted(got)}")
    missing = {norm(h) for h in re.findall(r"#[0-9a-fA-F]{6}", (ROOT / "docs/design.md").read_text())} - COLORS
    ok &= not missing
    print(f"{'ok  ' if not missing else 'FAIL'} design.md hex ⊂ rules.json colors: missing={sorted(missing)}")
    return ok


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) != 3 or sys.argv[2] not in FILES:
        sys.exit(__doc__)
    slug, gate = sys.argv[1:]
    res = judge(gate, ROOT / "runs" / slug / FILES[gate])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res["pass"] else 1)
