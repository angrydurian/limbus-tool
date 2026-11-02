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
    crop=im.crop((12,28,sep-2,min(168,h)))
    fn=by[name].get("icon") or nextname()
    crop.save(os.path.join("gifts/icons",fn));by[name]["icon"]=fn;print(name,"→",fn,crop.size)
json.dump(d,open(p,"w",encoding="utf8"),ensure_ascii=False,indent=1)
