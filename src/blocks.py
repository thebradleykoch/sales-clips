import json
def skip_txt(s):
    m,x=divmod(int(round(s)),60)
    return "Skipped ahead "+(f"{m} min {x} sec" if m and x else f"{m} min" if m else f"{x} sec")
def make_blocks(pre):
    """Turn a baked clip list into an ordered block list: markers (clip starts + highlights) and speaker turns."""
    hl_by_clip={}
    for h in pre["hl"]:
        ws=[w for t in pre["clips"][h["clip"]]["turns"] for w in t["words"] if "s" in w]
        w=min(ws,key=lambda w:abs(w["s"]-h["src"]))
        hl_by_clip.setdefault(h["clip"],[]).append((w["t"],h["label"]))
    blocks=[]
    for ci,c in enumerate(pre["clips"]):
        if ci>0 and c["skip"] and c["skip"]>2:
            blocks.append({"type":"note","text":c.get("note_override") or ("[Transcript jumps ahead to next highlight]" if c["label"] else "[Transcript jumps ahead]"),"t":c["t0"],"clip":ci})
        if c["label"]:
            blocks.append({"type":"marker","label":c["label"],"t":c["t0"],"note":"","clip":ci})
        hls=sorted(hl_by_clip.get(ci,[]))
        for t in c["turns"]:
            cur={"type":"turn","sp":t["sp"],"words":[],"clip":ci}
            for w in t["words"]:
                hit=[h for h in hls if abs(h[0]-w["t"])<0.005]
                if hit:
                    if cur["words"]: blocks.append(cur)
                    blocks.append({"type":"marker","label":hit[0][1],"t":w["t"],"note":"","clip":ci})
                    hls.remove(hit[0])
                    cur={"type":"turn","sp":t["sp"],"words":[],"clip":ci}
                rm=1 if (w["w"].startswith("[") and w["w"].endswith("removed]")) else 0
                cur["words"].append([w["w"],w["t"],rm,1 if w.get("n") else 0])
            if cur["words"]: blocks.append(cur)
        assert not hls, hls
    return blocks
