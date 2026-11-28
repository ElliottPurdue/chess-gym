import json, random, collections, chess, chess.engine
random.seed(3)
S=[];T=[]
for f in ['out0.json','out1.json']:
    d=json.load(open(f)); S+=d['safe']; T+=d['threat']
def lastcap(x):
    if not x['last']: return False
    b=chess.Board(x['fen']); b.pop() if False else None
    # reconstruct: a capture is likely if the destination square of last move holds an opponent piece and... we can't pop from FEN; use material heuristic below
    return None
eng=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish'); eng.configure({'Threads':4,'Hash':256})
def gid(x): return x['id'].split('-')[1]
# threat: drop the mid-exchange ones. Detect: in the real position, is there a recapture on the last-move square that is my best move?
outT=[]; per=collections.Counter()
T.sort(key=lambda x:-x['date'])
for x in T:
    if per[gid(x)]>=3 or not (250<=x['drop']<=1500): continue
    b=chess.Board(x['fen'])
    if x['last']:
        to=chess.parse_square(x['last'][2:4])
        best=eng.analyse(b, chess.engine.Limit(depth=12))['pv'][0]
        if best.to_square==to and b.is_capture(best): continue   # mid-exchange: the real answer is just recapture
    nb=b.copy(); nb.push(chess.Move.null())
    me=b.turn
    infos=eng.analyse(nb, chess.engine.Limit(depth=14), multipv=3)
    e0=eng.analyse(b, chess.engine.Limit(depth=14))['score'].pov(me).score(mate_score=3000)
    sc=[(i['score'].pov(me).score(mate_score=3000), i['pv']) for i in infos]
    if e0-sc[0][0]<250: continue
    acc=sorted({pv[0].uci() for s,pv in sc if e0-s>=200})
    x['threat']=sc[0][1][0].uci(); x['threatSan']=nb.san(sc[0][1][0]); x['line']=nb.variation_san(sc[0][1][:4]); x['acc']=acc; x['drop']=e0-sc[0][0]
    x['mate']=sc[0][0]<=-2000
    outT.append(x); per[gid(x)]+=1
    if len(outT)>=160: break
outS=[]; per=collections.Counter()
S.sort(key=lambda x:-x['date'])
uns=[x for x in S if not x['safe']]; sf=[x for x in S if x['safe']]
for pool,cap in ((uns,100),(sf,70)):
    n=0
    for x in pool:
        if per[gid(x)]>=3: continue
        if not x['safe']:
            # confirm with a deeper look that the move really loses
            b=chess.Board(x['fen']); me=b.turn; e0=eng.analyse(b, chess.engine.Limit(depth=14))['score'].pov(me).score(mate_score=3000)
            b.push(chess.Move.from_uci(x['move'])); i=eng.analyse(b, chess.engine.Limit(depth=14)); e1=i['score'].pov(me).score(mate_score=3000)
            if e0-e1<180: continue
            x['reply']=i['pv'][0].uci(); x['replySan']=b.san(i['pv'][0]); x['line']=b.variation_san(i['pv'][:4]); x['loss']=e0-e1
        outS.append(x); per[gid(x)]+=1; n+=1
        if n>=cap: break
eng.quit()
for x in outS+outT: x.pop('date',None)
random.shuffle(outS); random.shuffle(outT)
json.dump(dict(safe=outS, threat=outT), open('/home/claude/gym/work/drills.json','w'), separators=(',',':'))
print(len(outS), collections.Counter(x['safe'] for x in outS), len(outT), sum(x['mate'] for x in outT), collections.Counter(len(x['acc']) for x in outT))
