#!/usr/bin/env python3
"""하네스 판정자. 기준은 rules/rules.json 하나뿐.

사용법:
  python3 scripts/judge.py <slug> <G1|G2|S3|S4>          runs/<slug>/ 산출물 판정
  python3 scripts/judge.py <slug> <S3|S4> --live < dump  Figma에서 방금 뽑은 덤프(stdin)로 판정 + 저장된 덤프와 대조
  python3 scripts/judge.py --next <slug>                 gate-log.md로 다음 단계·복귀 횟수 계산
  python3 scripts/judge.py --selftest                    tests/fixtures + design.md 색 동기화 검사
판정 출력: {"gate","pass","violations":[{"node","rule","value"}]} JSON. 통과 0, 실패 1로 종료.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "rules/rules.json").read_text())
FILES = {"G1": "s1-research.md", "G2": "s2-spec.md", "S3": "s3-keyscreens.json", "S4": "s4-system.json"}


def v(rule, value, node="-"):
    return {"node": node, "rule": rule, "value": value}


def norm(c):
    return c.lower().replace(" ", "")


def squash(s):
    return re.sub(r"\s", "", s)


COLORS = {norm(c) for c in R["colors"]}


def pii(text, where):
    return [v("rule_B", m.group(), where) for p in R["rule_B"]["pii_regex"] for m in re.finditer(p, text)]


def check_g1(text):
    out, seen = [], set()
    rs = R["research"]
    refs = re.split(r"^## ", text, flags=re.M)[1:]
    lo, hi = rs["refs"]
    if not lo <= len(refs) <= hi:
        out.append(v("refs", len(refs)))
    for ref in refs:
        title = ref.splitlines()[0].strip()
        m = re.search(rs["link_regex"], ref)
        if not m:
            out.append(v("uibowl_link", 0, title))
        else:
            if m.group() in seen:
                out.append(v("duplicate_link", m.group(), title))
            seen.add(m.group())
            app = unquote(m.group(1))
            if squash(app) not in squash(title):  # 링크 속 앱 이름이 제목에 있어야 한다
                out.append(v("link_app_mismatch", app, title))
        points = re.findall(r"^- 반영:\s*\S", ref, re.M)
        if len(points) < rs["min_points_per_ref"]:
            out.append(v("points", len(points), title))
    return out


def check_g2(text):
    out = []
    a = R["rule_A"]
    screens = re.split(r"^## 화면:", text, flags=re.M)[1:]
    lo, hi = R["spec"]["screens"]
    if not lo <= len(screens) <= hi:
        out.append(v("screens", len(screens)))
    for s in screens:
        name = s.splitlines()[0].strip()
        fields = dict(re.findall(r"^- ([^:\n]+):[ \t]*(.*)$", s, re.M))
        for f in R["spec"]["required_fields"]:
            if not fields.get(f, "").strip():
                out.append(v("required_field", f, name))
        if a["sale_request_text"] in squash(s) and a["sale_request_role"] not in fields.get("권한", ""):
            out.append(v("rule_A", fields.get("권한", ""), name))
        for st in re.split(r"[,/]", fields.get("자산 상태", "")):
            if st.strip() and st.strip() not in a["asset_status"]:
                out.append(v("rule_A", st.strip(), name))
    for word in a["phase2_text"]:
        out += [v("rule_A", word)] * squash(text).count(word)
    return out + pii(text, "s2-spec.md")


def radius_ok(n, r):
    w, h = n.get("width", 0), n.get("height", 0)
    if r in R["radius"] or (w and h and r >= min(w, h) / 2):  # Figma는 높이/2 이상을 pill로 그린다
        return True
    is_icon = "app-icon-squircle" in f"{n.get('component', '')} {n.get('name', '')}"
    return is_icon and abs(r - R["radius_icon_ratio"] * w) <= 0.5


def check_frames(data, s4):
    out = []
    fr, font, acc = R["frame"], R["font"], R["accent"]
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
            label = f"{comp or ''} {n.get('name', '')}".lower()
            colors = n.get("fills", []) + n.get("strokes", [])
            for c in colors:
                if norm(c) not in COLORS:
                    out.append(v("color", c, nid))
            if norm(acc["value"]) in map(norm, colors):
                accent += 1
                if any(k in label for k in acc["forbidden_name_contains"]):
                    out.append(v("accent_on_cta", label.strip(), nid))
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
        if accent > acc["max_per_frame"]:
            out.append(v("accent_count", accent, f["id"]))
    if s4:
        for key in ("variables", "components"):
            if not data.get(key):
                out.append(v(f"no_{key}", 0))
    return out


def judge(gate, path, live=None):
    """live: Figma에서 방금 뽑은 덤프. 주어지면 그걸로 판정하고, 저장된 덤프가 다르면 dump_mismatch."""
    path = Path(path)
    if live is None and not path.exists():
        return {"gate": gate, "pass": False, "violations": [v("missing_file", str(path))]}
    if gate == "G1":
        out = check_g1(path.read_text())
    elif gate == "G2":
        out = check_g2(path.read_text())
    else:
        data = json.loads(path.read_text()) if live is None else live
        out = check_frames(data, s4=gate == "S4")
        if live is not None:
            saved = json.loads(path.read_text()) if path.exists() else None
            keys = ("frames", "variables", "components")
            if saved is None or any(saved.get(k) != live.get(k) for k in keys):
                out.append(v("dump_mismatch", "saved dump != live Figma", str(path)))
    return {"gate": gate, "pass": not out, "violations": out}


# gate-log.md 한 줄: | # | 시각 | 단계(G1|G2|S3|H1|S4) | PASS|FAIL | 메모 |
ON_PASS = {"G1": "S2", "G2": "S3", "S3": "H1", "H1": "S4", "S4": "DONE"}
ON_FAIL = {"G1": "S1", "G2": "S2", "S3": "S3", "H1": "S2", "S4": "S4"}


def next_step(log_text):
    rows = re.findall(r"^\|\s*\d+\s*\|[^|]*\|\s*(G1|G2|S3|H1|S4)\s*\|\s*(PASS|FAIL)\s*\|", log_text, re.M)
    retries = {}
    for step, res in rows:
        if res == "FAIL":
            retries[ON_FAIL[step]] = retries.get(ON_FAIL[step], 0) + 1
    if not rows:
        nxt = "S1"
    else:
        step, res = rows[-1]
        nxt = (ON_PASS if res == "PASS" else ON_FAIL)[step]
    stop = retries.get(nxt, 0) > R["retry_limit"]
    return {"next": "STOP" if stop else nxt, "retries": retries, "rows": len(rows)}


# 픽스처별로 반드시 잡혀야 하는 규칙. 엉뚱한 이유로 FAIL해도 셀프테스트가 걸러낸다.
EXPECT = {
    "G1-pass.md": set(), "G1-fail.md": {"refs"}, "G1-fail-link.md": {"duplicate_link", "link_app_mismatch"},
    "G2-pass.md": set(), "G2-fail-A.md": {"rule_A"}, "G2-fail-A-space.md": {"rule_A"},
    "G2-fail-B.md": {"rule_B"}, "G2-fail-B-space.md": {"rule_B"},
    "S3-pass.json": set(), "S3-fail.json": {"radius", "shadow"}, "S3-fail-cta.json": {"accent_on_cta"},
    "S4-pass.json": set(), "S4-fail.json": {"unbound_color"},
}
NEXT_EXPECT = {"gate-log-resume.md": "H1", "gate-log-stop.md": "STOP", "gate-log-empty.md": "S1"}


def selftest():
    fx = ROOT / "tests/fixtures"
    ok = True

    def report(good, msg):
        nonlocal ok
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {msg}")

    for name, want in EXPECT.items():
        res = judge(name.split("-")[0], fx / name)
        got = {x["rule"] for x in res["violations"]}
        report(res["pass"] if not want else want <= got, f"{name}: pass={res['pass']} rules={sorted(got)}")
    same = judge("S3", fx / "S3-pass.json", live=json.loads((fx / "S3-pass.json").read_text()))
    report(same["pass"], "live == saved dump → PASS")
    diff = judge("S3", fx / "S3-pass.json", live=json.loads((fx / "S3-fail.json").read_text()))
    report("dump_mismatch" in {x["rule"] for x in diff["violations"]}, "live != saved dump → dump_mismatch")
    for name, want in NEXT_EXPECT.items():
        got = next_step((fx / name).read_text())["next"]
        report(got == want, f"--next {name}: {got} (want {want})")
    missing = {norm(h) for h in re.findall(r"#[0-9a-fA-F]{6}", (ROOT / "docs/design.md").read_text())} - COLORS
    report(not missing, f"design.md hex ⊂ rules.json colors: missing={sorted(missing)}")
    return ok


def main(args):
    if args == ["--selftest"]:
        return 0 if selftest() else 1
    if len(args) == 2 and args[0] == "--next":
        log = ROOT / "runs" / args[1] / "gate-log.md"
        print(json.dumps(next_step(log.read_text() if log.exists() else ""), ensure_ascii=False))
        return 0
    if len(args) in (2, 3) and args[1] in FILES and (len(args) == 2 or (args[2] == "--live" and args[1] in ("S3", "S4"))):
        slug, gate = args[:2]
        live = json.load(sys.stdin) if len(args) == 3 else None
        res = judge(gate, ROOT / "runs" / slug / FILES[gate], live)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["pass"] else 1
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
