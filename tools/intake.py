"""깃허브 이슈 양식(.github/ISSUE_TEMPLATE) 내용 → 데이터 반영. 자동 처리(.github/workflows/intake.yml)가 부른다.
사용: python3 -I tools/intake.py gift|db 이슈본문.md 보고서.md
  gift: 위키 글 → parse_gifts.py, 캡처 → add_icon.py, 팩 지정 → set_pack.py, make_md.py
  db:   인격·E.G.O 캡처 JSON({"identity":..} / {"ego":..}) 또는 사이트 '변경분 복사' JSON → apply_pending.py
끝나면 보고서.md에 결과를 쓰고, 문제가 있으면 종료 코드 1 (자동 처리는 이때 커밋하지 않는다).
저장소 맨 위 폴더에서 실행한다."""
import json, os, re, subprocess, sys, tempfile, time, urllib.request, importlib.util

ROOT = os.getcwd()
SINNERS = ["이상", "파우스트", "돈키호테", "료슈", "뫼르소", "홍루", "히스클리프", "이스마엘", "로쟈", "싱클레어", "오티스", "그레고르"]
GRADES = ["ZAYIN", "TETH", "HE", "WAW", "ALEPH"]
EMPTY = {"", "_No response_", "None"}


class Fail(Exception):
    pass


def sections(body):
    """이슈 양식 본문('### 칸 이름' 아래 내용) → {칸 이름: 내용}"""
    out, cur = {}, None
    for line in body.replace("\r\n", "\n").split("\n"):
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m and m.group(1) in LABELS:
            cur = m.group(1); out[cur] = []; continue
        if cur: out[cur].append(line)
    res = {}
    for k, v in out.items():
        t = "\n".join(v).strip()
        res[k] = "" if t in EMPTY else t
    return res


LABELS = {"위키 글", "아이콘 캡처", "아이콘 대상 이름", "팩 지정", "JSON", "메모"}


def run(args):
    r = subprocess.run([sys.executable, "-I"] + args, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise Fail(f"`{' '.join(os.path.basename(a) for a in args[:1])}` 실행 오류:\n```\n{(r.stderr or r.stdout)[-1500:]}\n```")
    return r.stdout


def image_urls(text):
    urls = re.findall(r"!\[[^\]]*\]\((https?://[^)\s]+)\)", text)
    urls += re.findall(r"<img[^>]*\ssrc=[\"'](https?://[^\"']+)[\"']", text)
    # 순서대로(글에 나온 순서) 정렬
    return sorted(set(urls), key=text.index)


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": "limbus-tool-intake"})
    tok = os.environ.get("GH_TOKEN")
    if tok and url.startswith("https://github.com/"):  # 비공개 저장소 첨부 대비(공개면 없어도 됨)
        req.add_header("Authorization", "token " + tok)
    for n in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
                f.write(r.read()); return
        except Exception as e:
            err = e; time.sleep(2 * (n + 1))
    raise Fail(f"캡처를 받지 못했어요: {url} ({err})")


def load_gifts():
    return {g["name"]: g for g in json.load(open("gifts/gifts.json", encoding="utf8"))["gifts"]}


def gift(body, rep):
    s = sections(body)
    text, pics, names_txt, packs_txt = s.get("위키 글", ""), s.get("아이콘 캡처", ""), s.get("아이콘 대상 이름", ""), s.get("팩 지정", "")
    spec = importlib.util.spec_from_file_location("parse_gifts", os.path.join(ROOT, "gifts/parse_gifts.py"))
    pg = importlib.util.module_from_spec(spec); spec.loader.exec_module(pg)
    parsed = pg.parse(text) if text else []
    if text and not parsed:
        raise Fail("위키 글에서 기프트를 찾지 못했어요. 첫 줄이 `Ⅳ 기프트 이름`처럼 등급 + 이름으로 시작하는지 확인해 주세요.")
    before = load_gifts()
    pnames = [g["name"] for g in parsed]
    # 아이콘 대상: 따로 적었으면 그 순서, 아니면 위키 글의 기프트 순서
    targets = [x.strip() for x in re.split(r"[\n,]", names_txt) if x.strip()] if names_txt else pnames
    urls = image_urls(pics)
    if not parsed and not urls and not packs_txt:
        raise Fail("넣을 내용이 없어요. 위키 글이나 아이콘 캡처, 팩 지정 중 하나는 있어야 해요.")
    if urls and len(urls) != len(targets):
        raise Fail(f"캡처 수({len(urls)}장)와 기프트 수({len(targets)}개: {', '.join(targets) or '없음'})가 달라요. "
                   "캡처를 기프트 순서대로 하나씩 넣거나 '아이콘 대상 이름' 칸에 이름을 순서대로 적어 주세요.")
    packs = []
    for line in packs_txt.splitlines():
        if not line.strip(): continue
        m = re.match(r"^\s*(.+?)\s*=\s*(.+?)\s*$", line)
        if not m: raise Fail(f"팩 지정 줄 형식이 달라요: `{line}` → `기프트 이름 = 팩 이름`으로 적어 주세요.")
        packs.append((m.group(1), m.group(2)))
    known = set(before) | set(pnames)
    miss = [n for n in targets[:len(urls)] if n not in known] + [n for n, _ in packs if n not in known]
    if miss: raise Fail("없는 기프트 이름: " + ", ".join(miss) + " (위키 글에도, 기존 데이터에도 없어요)")
    # 1) 글
    if parsed:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf8") as f:
            f.write(text); tp = f.name
        run(["gifts/parse_gifts.py", tp])
    # 2) 아이콘
    if urls:
        tmp = tempfile.mkdtemp(); args = []
        for i, (u, n) in enumerate(zip(urls, targets)):
            p = os.path.join(tmp, f"{i}.png"); download(u, p); args += [p, n]
        out = run(["gifts/add_icon.py"] + args)
        if "없는 기프트" in out: raise Fail("아이콘을 붙이지 못했어요:\n```\n" + out + "\n```")
    # 3) 팩
    for n, pk in packs: run(["gifts/set_pack.py", pk, n])
    # 4) 검사
    after = load_gifts(); probs = []; warns = []
    touched = list(dict.fromkeys(pnames + targets[:len(urls)] + [n for n, _ in packs]))
    for n in touched:
        g = after[n]
        if not g.get("tier"): probs.append(f"{n}: 등급 없음")
        if g.get("price") is None: probs.append(f"{n}: 코스트(가격) 없음")
        if not g["effects"]["base"]: probs.append(f"{n}: 효과 없음")
        if not g.get("icon"): warns.append(f"{n}: 아이콘이 아직 없어요 (캡처를 따로 보내 주세요)")
        for r in g.get("recipe") or []:
            if r not in after: warns.append(f"{n}: 조합 재료 '{r}'가 아직 데이터에 없어요")
    if probs: raise Fail("검사에서 걸렸어요:\n" + "\n".join("- " + p for p in probs))
    run(["gifts/make_md.py"])
    added = [n for n in touched if n not in before]
    changed = [n for n in touched if n in before and before[n] != after[n]]
    same = [n for n in touched if n in before and before[n] == after[n]]
    rep += [f"**기프트** 추가 {len(added)}개 · 수정 {len(changed)}개 · 변경 없음 {len(same)}개 (총 {len(after)}개)", ""]
    if added or changed:
        rep += ["| | 기프트 | 등급 | 키워드 | 가격 | 효과(기본/+/++) | 팩 | 아이콘 |", "|---|---|---|---|---|---|---|---|"]
        for n in added + changed:
            g = after[n]; e = g["effects"]
            rep.append(f"| {'추가' if n in added else '수정'} | {n} | {g.get('tier')} | {g.get('keyword') or '없음'} | {g.get('price')} | "
                       f"{len(e['base'])}/{len(e['plus'])}/{len(e['plus2'])} | {', '.join(g.get('pack') or []) or '-'} | {g.get('icon') or '없음'} |")
        rep.append("")
    if warns: rep += ["참고:"] + ["- " + w for w in warns] + [""]
    return added + changed


def json_values(text):
    text = re.sub(r"^```[a-zA-Z]*\s*$", "", text, flags=re.M)  # 코드 블록 표시 제거
    dec, i, out = json.JSONDecoder(), 0, []
    while True:
        while i < len(text) and text[i] not in "{[": i += 1
        if i >= len(text): break
        try:
            v, j = dec.raw_decode(text, i)
        except json.JSONDecodeError as e:
            line = text.count("\n", 0, e.pos) + 1
            raise Fail(f"JSON 문법 오류 ({line}번째 줄 근처): {e.msg}. 괄호·쉼표·따옴표를 확인해 주세요.")
        out += v if isinstance(v, list) else [v]; i = j
    return out


def check_identity(x, tag):
    p = []
    if not x.get("name"): p.append("name 없음")
    if x.get("sinner") not in SINNERS: p.append(f"sinner '{x.get('sinner')}'는 수감자 이름이 아님")
    if x.get("rarity") not in (1, 2, 3): p.append("rarity는 1~3")
    sk = x.get("skills")
    if not isinstance(sk, list) or not sk: p.append("skills 없음")
    else:
        slots = [s.get("slot") for s in sk]
        for need in ("S1", "S2", "S3"):
            if need not in slots: p.append(f"{need} 스킬 없음")
        bad = [s for s in slots if s not in ("S1", "S2", "S3", "DEF", "S1x", "S2x", "S3x", "DEF2")]
        if bad: p.append("알 수 없는 slot: " + ", ".join(map(str, bad)))
    return [f"{tag}: {m}" for m in p]


def check_ego(x, tag):
    p = []
    if not x.get("name"): p.append("name 없음")
    if x.get("sinner") not in SINNERS: p.append(f"sinner '{x.get('sinner')}'는 수감자 이름이 아님")
    if x.get("grade") not in GRADES: p.append("grade는 ZAYIN/TETH/HE/WAW/ALEPH")
    c = x.get("cost")
    if not isinstance(c, list) or not all(isinstance(v, list) and len(v) == 2 for v in c): p.append('cost는 [["분노",2],...] 형식')
    if not isinstance(x.get("awaken"), dict): p.append("awaken(각성 스킬) 없음")
    for k, v in (x.get("res") or {}).items():
        if v not in ("취약", "보통", "내성"): p.append(f"res.{k} 값 '{v}'는 취약/보통/내성이 아님")
    return [f"{tag}: {m}" for m in p]


def db(body, rep):
    s = sections(body)
    vals = json_values(s.get("JSON", ""))
    if not vals: raise Fail("JSON 칸이 비었어요.")
    cur = {n: {x["id"]: x for x in json.load(open(f"data/db/{n}.json", encoding="utf8"))[n]} for n in ("identities", "egos", "recs")}
    pend = {"identities": {}, "egos": {}, "recs": {}}; probs = []; notes = []
    for v in vals:
        if not isinstance(v, dict): probs.append("JSON 하나가 객체({...})가 아니에요"); continue
        if any(k in v for k in ("identities", "egos", "recs")) and not ("identity" in v or "ego" in v):  # 사이트 '변경분 복사'
            for n in ("identities", "egos", "recs"):
                for i, w in (v.get(n) or {}).items():
                    if not isinstance(w, dict): probs.append(f"{n}.{i}: 형식 오류"); continue
                    if w.get("deleted"):
                        if i not in cur[n]: probs.append(f"{n}.{i}: 지울 항목이 없어요")
                    elif n != "recs":
                        d = w.get("data")
                        if not isinstance(d, dict): probs.append(f"{n}.{i}: data 없음"); continue
                        probs += (check_identity if n == "identities" else check_ego)(d, f"{d.get('sinner')} {d.get('name')}")
                    pend[n][i] = w
            continue
        kind = "identities" if "identity" in v else "egos" if "ego" in v else None
        if not kind: probs.append('JSON에 "identity"나 "ego"가 없어요'); continue
        x = dict(v["identity" if kind == "identities" else "ego"])
        tag = f"{x.get('sinner')} {x.get('name')}"
        unc = v.get("uncertain") or []
        if unc: probs.append(f"{tag}: 확인 필요(uncertain) 항목이 남아 있어요 → {', '.join(map(str, unc))}. 값을 확인해 채우고 uncertain을 비워 주세요.")
        probs += (check_identity if kind == "identities" else check_ego)(x, tag)
        key = lambda y: (y.get("sinner"), re.sub(r"\s", "", y.get("name") or ""))
        eid = v.get("existingId") or x.get("id")
        if eid and eid not in cur[kind]: probs.append(f"{tag}: existingId '{eid}'가 데이터에 없어요"); continue
        if not eid:
            same = [i for i, y in cur[kind].items() if key(y) == key(x)]
            if same: eid = same[0]; notes.append(f"{tag}: 같은 이름이 이미 있어서 기존 항목({eid})을 고쳐요")
        if not eid:
            eid = ("c-" if kind == "identities" else "e-") + base36(int(time.time() * 1000) + len(pend[kind]))
        x.pop("id", None)
        if kind == "identities": x.setdefault("src", "capture")
        pend[kind][eid] = {"data": x}
    if probs: raise Fail("검사에서 걸렸어요:\n" + "\n".join("- " + p for p in probs))
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf8") as f:
        json.dump(pend, f, ensure_ascii=False); tp = f.name
    run(["tools/apply_pending.py", tp])
    after = {n: {x["id"]: x for x in json.load(open(f"data/db/{n}.json", encoding="utf8"))[n]} for n in ("identities", "egos", "recs")}
    names = {"identities": "인격", "egos": "E.G.O", "recs": "추천 덱"}
    rows, done = [], []
    for n, items in pend.items():
        for i, w in items.items():
            b, a = cur[n].get(i), after[n].get(i)
            what = "삭제" if a is None else "추가" if b is None else "변경 없음" if a == b else "수정"
            y = a or b or {}
            rows.append(f"| {what} | {names[n]} | {y.get('sinner', '')} | {y.get('name', '')} | `{i}` |")
            if what != "변경 없음": done.append(i)
    rep += [f"**인격·E.G.O** 반영 {len(done)}개 / 받은 항목 {len(rows)}개 (인격 {len(after['identities'])} · E.G.O {len(after['egos'])} · 추천 덱 {len(after['recs'])})", "",
            "| | 종류 | 수감자 | 이름 | id |", "|---|---|---|---|---|"] + rows + [""]
    if notes: rep += ["참고:"] + ["- " + m for m in notes] + [""]
    return done


def base36(n):
    s = ""
    while n: n, r = divmod(n, 36); s = "0123456789abcdefghijklmnopqrstuvwxyz"[r] + s
    return s or "0"


if __name__ == "__main__":
    kind, src, dst = sys.argv[1:4]
    body = open(src, encoding="utf8").read(); rep = []
    try:
        changed = (gift if kind == "gift" else db)(body, rep)
        head = "✅ 반영했어요. main에 커밋합니다." if changed else "☑️ 바뀐 내용이 없어서 커밋하지 않았어요."
        open(dst, "w", encoding="utf8").write(head + "\n\n" + "\n".join(rep) + "\n사이트에는 다음 버전 때 들어가요.\n")
        open(dst + ".count", "w").write(str(len(changed)))
    except Fail as e:
        open(dst, "w", encoding="utf8").write("❌ 반영하지 못했어요. 데이터는 그대로예요.\n\n" + str(e) +
                                             "\n\n이슈 내용을 고쳐서 저장하면 다시 처리해요.\n")
        sys.exit(1)
