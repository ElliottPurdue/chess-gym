import json, io, sys, random, urllib.request, chess, chess.pgn, chess.engine
part, nparts = int(sys.argv[1]), int(sys.argv[2])
F={"mmgisgoat69","fire_starter08","husamelhamravl","chefachille","bobsquad12390"}
def get(u):
    r=urllib.request.Request(u,headers={"User-Agent":"ElliottPurdue-training-analysis"}); return json.load(urllib.request.urlopen(r,timeout=60))
games=[]
for u in get("https://api.chess.com/pub/player/elliottpurdue/games/archives")["archives"]: games+=get(u).get("games",[])
games=[g for g in games if g.get('rules')=='chess']
games.sort(key=lambda g:g['end_time'])
eng=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish'); eng.configure({'Threads':1,'Hash':64})
L=chess.engine.Limit(depth=12)
def ev(b, me):
    if b.is_checkmate(): return -3000 if b.turn==me else 3000
    if b.is_game_over(): return 0
    i=eng.analyse(b,L); return max(-1500,min(1500,i['score'].pov(me).score(mate_score=3000))), i.get('pv',[])
safe=[]; threat=[]
for gi,g in enumerate(games):
    if gi % nparts != part: continue
    meS='white' if g['white']['username'].lower()=='elliottpurdue' else 'black'; op='black' if meS=='white' else 'white'
    if g[op]['username'].lower() in F: continue
    me=chess.WHITE if meS=='white' else chess.BLACK
    pg=chess.pgn.read_game(io.StringIO(g['pgn'])); b=pg.board(); mv=list(pg.mainline_moves())
    gid=g['url'].rsplit('/',1)[-1]
    for i,m in enumerate(mv):
        if b.fullmove_number<6 or b.fullmove_number>40: b.push(m); continue
        if b.turn==me and not b.is_check():
            r=ev(b,me)
            if isinstance(r,tuple):
                e0,pv0=r
                if -400<e0<600:
                    # threat drill: what would they do if I passed?
                    nb=b.copy(); nb.push(chess.Move.null())
                    if not nb.is_check():
                        rn=ev(nb,me)
                        if isinstance(rn,tuple) and rn[1]:
                            en,pvn=rn; t=pvn[0]
                            if e0-en>=250:
                                threat.append(dict(id=f"t-{gid}-{i}", fen=b.fen(), last=mv[i-1].uci() if i else None, threat=t.uci(), threatSan=nb.san(t), line=nb.variation_san(pvn[:4]), drop=e0-en, mate=abs(en)>=1400, date=g['end_time']))
                    # safety drill: was my actual move safe?
                    b2=b.copy(); b2.push(m)
                    r2=ev(b2,me)
                    if isinstance(r2,tuple):
                        e1,pv1=r2; loss=e0-e1
                        opp_caps=any(b2.is_capture(x) or b2.gives_check(x) for x in b2.legal_moves)
                        if loss>=200 and pv1:
                            safe.append(dict(id=f"s-{gid}-{i}", fen=b.fen(), last=mv[i-1].uci() if i else None, move=m.uci(), moveSan=b.san(m), safe=False, reply=pv1[0].uci(), replySan=b2.san(pv1[0]), line=b2.variation_san(pv1[:4]), loss=loss, date=g['end_time']))
                        elif loss<=25 and opp_caps and random.random()<0.25:
                            safe.append(dict(id=f"s-{gid}-{i}", fen=b.fen(), last=mv[i-1].uci() if i else None, move=m.uci(), moveSan=b.san(m), safe=True, loss=loss, date=g['end_time']))
        b.push(m)
    print(gi, len(safe), len(threat), flush=True)
eng.quit()
json.dump(dict(safe=safe,threat=threat), open(f'/home/claude/drills/out{part}.json','w'))
print('done', flush=True)
