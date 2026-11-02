"""나무위키 기프트 상자를 글자로 복사한 텍스트 → gifts.json에 추가/갱신.
사용: python3 gifts/parse_gifts.py 붙여넣은.txt   (상자 여러 개를 이어 붙여도 됨)"""
import json,re,sys
TIERS={"1":"Ⅰ","2":"Ⅱ","3":"Ⅲ","4":"Ⅳ","5":"Ⅴ","EX":"EX","Ⅰ":"Ⅰ","Ⅱ":"Ⅱ","Ⅲ":"Ⅲ","Ⅳ":"Ⅳ","Ⅴ":"Ⅴ"}
KWS=["화상","출혈","진동","파열","침잠","호흡","충전","참격","관통","타격"]
LABELS={"연관","등급","첫 등장","강화 여부","효과","기본 효과","+","++","언어별 표기","기프트 상세 정보"}
def parse(text):
    lines=[re.sub(r"\[\d+\]","",l).strip() for l in text.splitlines()]  # 나무위키 각주 번호 제거
    lines=[l for l in lines if l]
    out=[];cur=None;sec=None
    def new(): return {"name":None,"tier":None,"keyword":None,"price":None,"source":"통상","limit":None,"related":None,"first":None,"upgrade":None,"effects":{"base":[],"plus":[],"plus2":[]}}
    i=0
    while i<len(lines):
        l=lines[i]
        m=re.match(r'^(Ⅰ|Ⅱ|Ⅲ|Ⅳ|Ⅴ|EX)\s+(.+)$',l)
        if m:
            if cur:out.append(cur)
            cur=new();cur["tier"]=m.group(1);cur["name"]=m.group(2).strip();sec=None;i+=1;continue
        if cur is None:i+=1;continue
        if l.startswith("림버스UI"):i+=1;continue
        m=re.match(r'^림버스컴퍼니\s+(\S+)\s+(.+)$',l)
        if m:
            if m.group(1)=="코스트":
                cur["price"]=int(re.sub(r'\D','',m.group(2).split("[")[0]) or 0)
                if "구매불가" in m.group(2):cur["buyable"]=False
            elif m.group(2) in KWS:cur["keyword"]=m.group(2)
            i+=1;continue
        if sec is None and len(l)<40 and ("한정" in l or "합성" in l):
            parts=[x.strip() for x in l.split(",")]
            cur["source"]="합성" if any("합성" in x for x in parts) else "한정"
            lim=[x for x in parts if "한정" in x];cur["limit"]=", ".join(lim) or None;i+=1;continue
        if l=="조합식":cur["recipe"]=[x.strip() for x in lines[i+1].split("+")];i+=2;continue
        if l=="연관":cur["related"]=lines[i+1];i+=2;continue
        if l=="등급":cur["tier"]=cur["tier"] or TIERS.get(lines[i+1]);i+=2;continue
        if l=="첫 등장":cur["first"]=lines[i+1];i+=2;continue
        if l=="강화 여부":cur["upgrade"]=lines[i+1]=="가능";i+=2;continue
        if l=="효과":sec="base";i+=1;continue
        if l=="기본 효과":sec="base";i+=1;continue
        if l=="+":sec="plus";i+=1;continue
        if l=="++":sec="plus2";i+=1;continue
        if l=="언어별 표기":sec="lang";i+=1;continue
        if l=="기프트 상세 정보":i+=1;continue
        if sec in("base","plus","plus2"):
            if l.startswith("(") and cur["effects"][sec]:cur["effects"][sec][-1]+=" "+l
            else:cur["effects"][sec].append(l)
        i+=1
    if cur:out.append(cur)
    for g in out:  # +/++ 효과가 있으면 강화 가능으로 봄(나무위키 "강화 여부" 칸 오타 대비)
        if g["effects"]["plus"] and g["upgrade"] is False:g["upgrade"]=True;g["note_fix"]="강화 여부 칸은 '불가'였지만 +/++ 효과가 있어 가능으로 저장"
    return out
if __name__=="__main__":
    p="gifts/gifts.json";d=json.load(open(p,encoding="utf8"))
    new=parse(open(sys.argv[1],encoding="utf8").read())
    by={g["name"]:g for g in d["gifts"]}
    for g in new:
        g["missing"]=[k for k in("tier","keyword","price") if g[k] is None and not(k=="keyword")]
        by[g["name"]]={**by.get(g["name"],{}),**{k:v for k,v in g.items() if v not in(None,[],{"base":[],"plus":[],"plus2":[]})}}
        print(g["name"],g["tier"],g["keyword"],g["price"],g["source"],g["limit"],len(g["effects"]["base"]),len(g["effects"]["plus"]),len(g["effects"]["plus2"]))
    d["gifts"]=sorted(by.values(),key=lambda g:("Ⅰ Ⅱ Ⅲ Ⅳ Ⅴ EX".split().index(g.get("tier") or "EX"),g["name"]))
    json.dump(d,open(p,"w",encoding="utf8"),ensure_ascii=False,indent=1);print("총",len(d["gifts"]))
