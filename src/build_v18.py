import json, sys, base64
sys.path.insert(0,'/home/claude/clips/scripts')
from blocks import make_blocks
from icons import icon
pre=json.load(open(sys.argv[1])); mp3=sys.argv[2]; out=sys.argv[3]; title=sys.argv[4]; heading=sys.argv[5]; audio=sys.argv[6]
blocks=json.load(open(sys.argv[7])) if len(sys.argv)>7 else make_blocks(pre)
data={"duration":pre["duration"],"me":"Bradley","blocks":blocks,"clips":[{"t0":c["t0"],"t1":c["t1"]} for c in pre["clips"]]}
src=("data:audio/mpeg;base64,"+base64.b64encode(open(mp3,'rb').read()).decode()) if audio=="inline" else audio
I={"PLAY":icon("play","filled"),"PAUSE":icon("pause","filled"),"VOL":icon("volume-high","line"),"VOLLOW":icon("volume-low","line"),
   "MUTE":icon("volume-slash","line"),"SEARCH":icon("search","line"),"UP":icon("chevron-up","line"),"DOWN":icon("chevron-down","line"),
   "TOC":icon("menu-2","line"),"CHECK":icon("check","line"),"JUMP":icon("arrow-bottom","line"),"SUN":icon("sun","line"),"MOON":icon("moon","line")}
h=open('/home/claude/clips/scripts/player_v18.html').read().replace("__TITLE__",title).replace("__HEADING__",heading)
for k,v in I.items(): h=h.replace(f"__I_{k}__",v)
h=h.replace("__ICONS_JSON__",json.dumps({k:I[k] for k in ["PLAY","PAUSE","VOL","VOLLOW","MUTE","CHECK","SUN","MOON"]}))
h=h.replace("__DATA__",json.dumps(data,ensure_ascii=False).replace("</","<\\/")).replace("__AUDIO_SRC__",src)
open(out,'w').write(h); print(out,len(h),sum(1 for b in blocks if b["type"]=="marker"),"markers")
