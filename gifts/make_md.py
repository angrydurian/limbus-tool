"""gifts.json → gifts.md (사람이 읽는 목록). 사용: python3 gifts/make_md.py"""
import json
d=json.load(open("gifts/gifts.json",encoding="utf8"))["gifts"]
KW=["화상","출혈","진동","파열","침잠","호흡","충전","참격","관통","타격",None]
TI="Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ EX".split()
out=["# 거울 던전 E.G.O 기프트","",f"출처: 나무위키 · 총 {len(d)}개 · `gifts.json`에서 자동 생성 (`python3 gifts/make_md.py`)",""]
cnt=[(k or "키워드 없음",sum(1 for g in d if g["keyword"]==k)) for k in KW]
out.append(" · ".join(f"{k} {n}" for k,n in cnt if n));out.append("")
for k in KW:
    gs=sorted([g for g in d if g["keyword"]==k],key=lambda g:(TI.index(g.get("tier") or "EX"),g["name"]))
    if not gs:continue
    out+=[f"## {k or '키워드 없음'} ({len(gs)})",""]
    for g in gs:
        src=g["source"]+(f" · {g['limit']}" if g.get("limit") else "")
        price=f"{g['price']}"+(" (구매불가)" if g.get("buyable") is False else "")+(f" ({g['price_note']})" if g.get("price_note") else "")
        out.append(f"### {g['tier']} {g['name']}")
        out.append("")
        if g.get("icon"):out+=[f"![{g['name']}](icons/{g['icon']})",""]
        out.append(f"- 가격: {price} · 획득: {src} · 강화: {'가능' if g.get('upgrade') else '불가'}")
        c=g.get("curse")
        if c:out.append(f"- {c['type']} 기프트"+(f" → 축복: {c.get('pair','(짝 미정)')}"+(f" (조건: {c['condition']})" if c.get('condition') else "") if c['type']=="저주" else f" ← 저주: {c.get('pair','(짝 미정)')}"))
        if g.get("pack"):out.append(f"- 전용 팩: {', '.join(g['pack'])}")
        if g.get("recipe"):out.append(f"- 조합식{('['+g['recipe_note']+']') if g.get('recipe_note') else ''}: {' + '.join(g['recipe'])}")
        if g.get("recipe_detail"):out.append(f"  - {g['recipe_detail']}")
        if g.get("recipe_pick"):out.append(f"  - 고를 수 있는 것 ({g['recipe_pick']['count']}개): {', '.join(g['recipe_pick']['from'])}")
        meta=[x for x in (g.get("related") and f"연관: {g['related']}", g.get("first") and f"첫 등장: {g['first']}") if x]
        if meta:out.append("- "+" · ".join(meta))
        out.append("")
        e=g["effects"]
        for lab,key in (("효과" if not e.get("plus") else "기본","base"),("+","plus"),("++","plus2")):
            if e.get(key):
                out.append(f"**{lab}**");out.append("")
                out+=[f"- {l}" for l in e[key]];out.append("")
cur=[g for g in d if (g.get("curse") or {}).get("type")=="저주"]
if cur:
    out+=["## 저주 → 축복 기프트","","저주 기프트를 가진 채로 조건을 채우면 축복 기프트로 바뀜 (위 목록에도 같이 들어 있음)",""]
    bn={g["name"]:g for g in d}
    for g in sorted(cur,key=lambda g:(TI.index(g.get("tier") or "EX"),g["name"])):
        p=g["curse"].get("pair");b=bn.get(p)
        out.append(f"- {g['tier']} {g['name']} → {(b['tier']+' '+p) if b else '(짝 미정)'}"+(f" · 조건: {g['curse']['condition']}" if g['curse'].get('condition') else ""))
    out.append("")
packs={}
for g in d:
    for pk in g.get("pack") or []:packs.setdefault(pk,[]).append(g)
if packs:
    out+=["## 팩 전용 기프트","","(위 키워드 목록에도 같이 들어 있음)",""]
    for pk in sorted(packs):
        gs=sorted(packs[pk],key=lambda g:(TI.index(g.get("tier") or "EX"),g["name"]))
        out+=[f"### {pk} ({len(gs)})",""]+[f"- {g['tier']} {g['name']} ({g['keyword'] or '키워드 없음'})" for g in gs]+[""]
open("gifts/gifts.md","w",encoding="utf8").write("\n".join(out))
print(len(out),"lines")
