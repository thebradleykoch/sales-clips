import json,re
P=json.load(open('/home/claude/icons/picks.json'))
import os
ROOT='/home/claude/icons/Anron Icons 10 (All SVGs Export)/'
def find(name,style):
    for r,ds,fs in os.walk(ROOT+style):
        for f in fs:
            if f.strip()==name+'.svg': return os.path.relpath(os.path.join(r,f),ROOT)
def icon(name, style):
    P.setdefault(style,{}).setdefault(name,find(name,style))
    s=open('/home/claude/icons/Anron Icons 10 (All SVGs Export)/'+P[style][name]).read()
    s=re.sub(r'<defs>.*?</defs>','',s,flags=re.S)
    s=re.sub(r'\sclip-path="url\(#[^)]*\)"','',s)
    s=s.replace('#2F384C','currentColor').replace('#2f384c','currentColor')
    s=re.sub(r'fill="#[0-9A-Fa-f]{3,6}"','fill="currentColor"',s)
    s=re.sub(r'stroke="#[0-9A-Fa-f]{3,6}"','stroke="currentColor"',s)
    s=s.replace('<svg ','<svg aria-hidden="true" class="ic" ',1)
    return s
if __name__=="__main__":
    for n in ["play","pause"]: print(icon(n,"filled")[:300])
    print(icon("volume-high","duotone")[:400])
