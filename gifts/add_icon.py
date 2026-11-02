"""나무위키 기프트 상자 윗부분 캡처 → 왼쪽 아이콘만 잘라 gifts/icons/gNNN.png로 저장하고 gifts.json에 연결.
사용: python3 gifts/add_icon.py 캡처.png "기프트 이름" [캡처.png "이름" ...]"""
import json,sys,os
from PIL import Image
p="gifts/gifts.json";d=json.load(open(p,encoding="utf8"));by={g["name"]:g for g in d["gifts"]}
used={g.get("icon") for g in d["gifts"]}
def nextname():
    i=1
    while f"g{i:03d}.png" in used:i+=1
    used.add(f"g{i:03d}.png");return f"g{i:03d}.png"
args=sys.argv[1:]
for src,name in zip(args[::2],args[1::2]):
    if name not in by:print("없는 기프트:",name);continue
    im=Image.open(src).convert("RGB");w,h=im.size;px=im.load()
    bright=lambda x,y:sum(px[x,y])>500
    sep=next((x for x in range(60,w) if sum(bright(x,y) for y in range(40,min(150,h)))>90),152)
    # 아이콘 칸 = 구분선 왼쪽. 위아래는 빨간/주황 띠(맨 아래 줄)와 바깥 여백을 빼고 정사각형으로
    def redrow(y):  # 아래 색 띠(빨강·주황·노랑·초록·청록·파랑 등) 또는 흰 여백
        n=0
        for x in range(5,sep-5):
            c=px[x,y];mx,mn=max(c),min(c)
            if (mx>110 and mx-mn>60) or mn>200:n+=1
        return n>(sep-10)*0.6
    bottom=next((y for y in range(h//2,h) if redrow(y)),h)  # 위에서부터 처음 만나는 색 띠 = 아이콘 칸 끝
    side=sep-2-8
    top=max(0,bottom-side-4)
    crop=im.crop((8,top,sep-2,bottom-4))
    # 가장자리의 흰 여백·갈색 테두리 줄은 깎아냄
    c=crop.load();cw,ch=crop.size
    edge=lambda pts:sum(1 for q in pts if sum(c[q])>450 or (c[q][0]>140 and 70<c[q][1]<150 and c[q][2]<100))>len(pts)*0.6
    l,t,r,b=0,0,cw-1,ch-1
    while t<b and edge([(x,t) for x in range(l,r+1)]):t+=1
    while b>t and edge([(x,b) for x in range(l,r+1)]):b-=1
    while l<r and edge([(l,y) for y in range(t,b+1)]):l+=1
    while r>l and edge([(r,y) for y in range(t,b+1)]):r-=1
    crop=crop.crop((l,t,r+1,b+1))
    fn=by[name].get("icon") or nextname()
    crop.save(os.path.join("gifts/icons",fn));by[name]["icon"]=fn;print(name,"→",fn,crop.size)
json.dump(d,open(p,"w",encoding="utf8"),ensure_ascii=False,indent=1)
