"""깃허브 데이터(data/db/identities.json, egos.json, recs.json) → limbus-tool.html 안의 GH_DB로 넣기 (v0.5)
사용: python3 -I tools/embed_db.py   (저장소 맨 위에서 실행)
사이트는 인격·E.G.O·추천 덱을 이 내장 데이터로 보여 준다. 데이터를 바꾼 뒤 이 도구를 돌리고 사이트를 다시 올린다."""
import json,re,datetime
H="limbus-tool.html"
db={}
for n in ("identities","egos","recs"):
    db[n]=json.load(open(f"data/db/{n}.json",encoding="utf8"))[n]
db["at"]=datetime.date.today().isoformat()
js=json.dumps(db,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
block=f"<script>/*GH_DATA_START*/const GH_DB={js};/*GH_DATA_END*/</script>"
s=open(H,encoding="utf8").read()
if "/*GH_DATA_START*/" in s:
    s=re.sub(r"<script>/\*GH_DATA_START\*/.*?/\*GH_DATA_END\*/</script>",lambda m:block,s,count=1,flags=re.S)
else:
    mark="<script>\n/* ================= v1.0: 동기화"
    assert mark in s,"삽입 위치를 못 찾음"
    s=s.replace(mark,block+"\n"+mark,1)
open(H,"w",encoding="utf8").write(s)
print("GH_DB:",{k:len(v) for k,v in db.items() if isinstance(v,list)},db["at"])
