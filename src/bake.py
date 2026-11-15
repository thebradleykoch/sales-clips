import json, sys, subprocess, re
spec=json.load(open(sys.argv[1])); T=json.load(open(sys.argv[2]))['segments']; wav=sys.argv[3]; outdir=sys.argv[4]
PII=spec["pii"]; GAP=1.0; TAIL=0.45
def in_pii(t):
    for a,b,l in PII:
        if a<=t<b: return (a,b,l)
    return None
# flag bracket notes
note=False
for w in T:
    b=w['body']
    if b.startswith('['): note=True
    w['n']=note
    if re.search(r'\][.,:;!?]*$',b): note=False
pieces=[]; clips=[]; out=0.0; prev_end=None
for ci,c in enumerate(spec["clips"]):
    ws=[w for w in T if c["start"]-0.01<=w["startTime"]<=c["end"]+0.01]
    if not ws: raise SystemExit(f"empty clip {c['label']}")
    A=max(0,ws[0]["startTime"]-0.2); last=ws[-1]
    B=max(last["endTime"],last["startTime"]+0.35)+0.15+TAIL
    nxt=[w for w in T if w["startTime"]>last["startTime"]+0.001]
    if nxt: B=min(B, max(nxt[0]["startTime"]+0.02, last["endTime"]+0.12))
    for a,b,l in PII:
        if A< a < B and a>last["startTime"]: B=a   # never run a tail into cut material
        if a<=A<b: A=b
    # subtract pii
    ivs=[[A,B]]
    for a,b,l in PII:
        nxt=[]
        for x,y in ivs:
            if b<=x or a>=y: nxt.append([x,y])
            else:
                if a>x: nxt.append([x,a])
                if b<y: nxt.append([b,y])
        ivs=nxt
    if ci>0: out+=GAP
    t0=out; maps=[]
    for k,(x,y) in enumerate(ivs):
        d=y-x; fi=0.3 if k==0 else 0.02; fo=min(TAIL,max(0.1,d*0.2)) if k==len(ivs)-1 else 0.02
        pieces.append((x,y,fi,fo, GAP if (k==len(ivs)-1 and ci<len(spec["clips"])-1) else 0))
        maps.append((x,y,out)); out+=d
    def mt(t):
        for x,y,o in maps:
            if x-1e-6<=t<=y+1e-6: return round(o+t-x,2)
        return None
    turns=[]; cur=None; lastpii=None
    for w in ws:
        p=in_pii(w["startTime"])
        if p and not p[2]:
            continue
        if p:
            if p[0]!=lastpii and cur is not None:
                cur["words"].append({"w":f"[{p[2]}]","t":mt(p[0]-0.01) or cur["words"][-1]["t"],"n":1})
            elif p[0]!=lastpii:
                cur={"sp":w["speaker"],"words":[{"w":f"[{p[2]}]","t":t0,"n":1}]}; turns.append(cur)
            lastpii=p[0]; continue
        t=mt(w["startTime"])
        if t is None: continue
        if cur is None or cur["sp"]!=w["speaker"]:
            cur={"sp":w["speaker"],"words":[]}; turns.append(cur)
        cur["words"].append({"w":w["body"],"t":t,"n":1 if w["n"] else 0,"s":w["startTime"]})
    skip=None if prev_end is None else round(c["start"]-prev_end)
    clips.append({"label":c["label"],"note":c["note"],"note_override":c.get("note") if c.get("note","").startswith("[") else None,"skip":skip,"t0":round(t0,2),"t1":round(out,2),"src":[c["start"],c["end"]],"turns":turns})
    prev_end=c["end"]
# highlights
hl=[]
for lab,t in spec["highlights"]:
    best=None
    for c in clips:
        for tu in c["turns"]:
            pass
    # map via clip maps: recompute
    for ci,c in enumerate(spec["clips"]):
        if c["start"]-0.3<=t<=c["end"]:
            w=min((w for w in T if abs(w["startTime"]-t)<1.0), key=lambda w:abs(w["startTime"]-t))
            # find its mapped time in clip turns by matching body+approx
            cand=[x for tu in clips[ci]["turns"] for x in tu["words"] if x["w"]==w["body"]]
            off=clips[ci]["t0"]
            # mapped time = nearest candidate to expected (no pii before in most cases)
            exp=None
            hl.append({"label":lab,"src":w["startTime"],"clip":ci,"body":w["body"]})
            break
    else: raise SystemExit(f"highlight {lab} outside clips")
json.dump({"pieces":pieces,"clips":clips,"hl":hl,"duration":round(out,2)},open(f"{outdir}/{spec['id']}_pre.json","w"))
fc=[]
for i,(x,y,fi,fo,gap) in enumerate(pieces):
    d=y-x
    fc.append(f"[0:a]atrim={x:.3f}:{y:.3f},asetpts=PTS-STARTPTS,afade=t=in:d={fi},afade=t=out:st={d-fo:.3f}:d={fo}"+(f",apad=pad_dur={gap}" if gap else "")+f"[s{i}]")
fcs=";".join(fc)+";"+"".join(f"[s{i}]" for i in range(len(pieces)))+f"concat=n={len(pieces)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[o]"
mp3=f"{outdir}/{spec['id']}.mp3"
subprocess.run(["ffmpeg","-v","error","-y","-i",wav,"-filter_complex",fcs,"-map","[o]","-map_metadata","-1","-ar","32000","-ac","1","-b:a","56k",mp3],check=True)
print(mp3, round(out,2), len(pieces),"pieces")
for c in clips: print(f"{c['t0']:7.2f}-{c['t1']:7.2f} {c['label']:24s} skip={c['skip']} words={sum(len(t['words']) for t in c['turns'])}")
