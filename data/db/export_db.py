"""사이트 저장 공간(db)에서 내려받은 문서 폴더 → data/db/identities.json, egos.json
사용: python3 -I data/db/export_db.py <내려받은 폴더>   (폴더 안에 identities/, egos/ 가 있어야 함)
삭제된 문서(deleted)는 빼고, 수감자 순 → 출시일 순으로 정렬한다. 사이트 원본은 db이고 이 파일은 사본이다."""
import json,os,sys
SIN="이상 파우스트 돈키호테 료슈 뫼르소 홍루 히스클리프 이스마엘 로쟈 싱클레어 오티스 그레고르".split()
GR="ZAYIN TETH HE WAW ALEPH".split()
src=sys.argv[1]
def load(col):
    out=[]
    for f in sorted(x for x in os.listdir(os.path.join(src,col)) if x.endswith(".json") and not x.startswith(".")):
        d=json.load(open(os.path.join(src,col,f),encoding="utf8"))
        if d.get("deleted") or not d.get("data"):continue
        x=d["data"];x.setdefault("id",f[:-5]);out.append(x)
    return out
ids=load("identities");ids.sort(key=lambda x:(SIN.index(x["sinner"]) if x.get("sinner") in SIN else 99,x.get("release") or "9999",x.get("name","")))
egos=load("egos");egos.sort(key=lambda x:(SIN.index(x["sinner"]) if x.get("sinner") in SIN else 99,GR.index(x["grade"]) if x.get("grade") in GR else 9,x.get("name","")))
for n,v in (("identities",ids),("egos",egos)):
    json.dump({"about":f"사이트 저장 공간(db) {n} 사본. 원본은 사이트 db, 고칠 때는 사이트 관리자 탭에서. export_db.py로 다시 만듦","count":len(v),n:v},open(f"data/db/{n}.json","w",encoding="utf8"),ensure_ascii=False,indent=1)
    print(n,len(v))
