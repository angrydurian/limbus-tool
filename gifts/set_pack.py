"""위키 글에 팩 이름이 없을 때 직접 지정. 사용: python3 gifts/set_pack.py "팩 이름" "기프트1" "기프트2" ...
같은 기프트에 여러 번 실행하면 팩이 목록으로 쌓임. 팩을 지우려면 --remove "팩 이름" ..."""
import json,sys
p="gifts/gifts.json";d=json.load(open(p,encoding="utf8"))
a=sys.argv[1:];rm=a[0]=="--remove"
if rm:a=a[1:]
pk,names=a[0],a[1:];by={g["name"]:g for g in d["gifts"]}
for n in names:
    if n not in by:print("없음:",n);continue
    l=by[n].get("pack") or []
    l=[x for x in l if x!=pk] if rm else (l if pk in l else l+[pk])
    if l:by[n]["pack"]=l
    else:by[n].pop("pack",None)
    print(n,"→",by[n].get("pack"))
json.dump(d,open(p,"w",encoding="utf8"),ensure_ascii=False,indent=1)
