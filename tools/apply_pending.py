"""사이트 관리자 탭 '깃허브 반영 대기'에서 복사한 변경분 JSON → data/db/*.json에 반영
사용: python3 -I tools/apply_pending.py 변경분.json
변경분 형식: {"identities":{id:{"data":{...}} 또는 {"deleted":true}}, "egos":{...}, "recs":{id:{...추천 덱 필드} 또는 {"deleted":true}}}"""
import json,sys,subprocess
p=json.load(open(sys.argv[1],encoding="utf8"))
for n in ("identities","egos","recs"):
    if not p.get(n):continue
    f=f"data/db/{n}.json";d=json.load(open(f,encoding="utf8"));by={x["id"]:x for x in d[n]};order=[x["id"] for x in d[n]]
    for i,v in p[n].items():
        if v.get("deleted"):by.pop(i,None);print(n,"삭제",i);continue
        x=dict(v["data"]) if n!="recs" else {k:w for k,w in v.items() if k!="id"}
        x["id"]=i
        if i not in by:order.append(i)
        by[i]=x;print(n,"추가/수정",i,x.get("name"))
    d[n]=[by[i] for i in order if i in by];d["count"]=len(d[n])
    json.dump(d,open(f,"w",encoding="utf8"),ensure_ascii=False,indent=1,sort_keys=True)  # 키 순서를 기존 파일과 같게
