"""기프트 데이터(gifts/gifts.json + gifts/icons) → limbus-tool.html 안의 GIFT_DB로 넣기 (v0.6)
사용: python3 -I tools/embed_gifts.py   (저장소 맨 위에서). 아이콘은 64px webp로 줄여 넣는다."""
import json,re,io,base64,datetime
from PIL import Image
H="limbus-tool.html"
d=json.load(open("gifts/gifts.json",encoding="utf8"))["gifts"]
KEEP=["name","tier","keyword","price","buyable","price_note","source","limit","pack","related","first","upgrade","effects","recipe","recipe_note","recipe_detail","recipe_pick","curse","hidden","icon"]
gifts=[{k:g[k] for k in KEEP if g.get(k) not in (None,[],{})} for g in d]
icons={}
for g in gifts:
    fn=g.get("icon")
    if not fn or fn in icons:continue
    im=Image.open(f"gifts/icons/{fn}").convert("RGB");im=im.resize((64,round(im.height*64/im.width)),Image.LANCZOS)
    b=io.BytesIO();im.save(b,"WEBP",quality=80);icons[fn]="data:image/webp;base64,"+base64.b64encode(b.getvalue()).decode()
db={"gifts":gifts,"icons":icons,"at":datetime.date.today().isoformat()}
js=json.dumps(db,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
block=f"<script>/*GIFT_DATA_START*/const GIFT_DB={js};/*GIFT_DATA_END*/</script>"
s=open(H,encoding="utf8").read()
if "/*GIFT_DATA_START*/" in s:s=re.sub(r"<script>/\*GIFT_DATA_START\*/.*?/\*GIFT_DATA_END\*/</script>",lambda m:block,s,count=1,flags=re.S)
else:
    mark="<script>/*GH_DATA_START*/";assert mark in s;s=s.replace(mark,block+"\n"+mark,1)
open(H,"w",encoding="utf8").write(s)
print("GIFT_DB:",len(gifts),"gifts,",len(icons),"icons,",len(js)//1024,"KB")
