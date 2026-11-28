import json, chess, chess.engine
eng=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish'); eng.configure({'Threads':4,'Hash':512})
def ev(b, me, d=18):
    if b.is_checkmate(): return 30000 if b.turn!=me else -30000
    if b.is_game_over(): return 0
    return eng.analyse(b, chess.engine.Limit(depth=d))['score'].pov(me).score(mate_score=30000)
def study(fen, goal, nsteps, d=22, prefer=None):
    b=chess.Board(fen); me=b.turn; steps=[]
    for k in range(nsteps):
        vals=[]
        for m in b.legal_moves:
            b2=b.copy(); b2.push(m); vals.append((ev(b2,me), m))
        vals.sort(key=lambda x:-x[0]); best=vals[0][0]
        if goal=='win': acc=[m.uci() for v,m in vals if v>=400 and (v>=best-4 if best>=20000 else v>=best-60)]
        else: acc=[m.uci() for v,m in vals if v>=-60]
        info=eng.analyse(b, chess.engine.Limit(depth=d)); play=info['pv'][0]
        if play.uci() not in acc: play=chess.Move.from_uci(acc[0])
        if prefer:
            pm=prefer(b, acc)
            if pm: play=chess.Move.from_uci(pm)
        b.push(play)
        if b.is_game_over(): steps.append(dict(acc=acc, play=play.uci(), reply=None)); break
        rep=eng.analyse(b, chess.engine.Limit(depth=d))['pv'][0]
        steps.append(dict(acc=acc, play=play.uci(), reply=rep.uci(), n=len(acc), tot=len(vals)))
        b.push(rep)
    return steps
LUC=['d1d4','b8c7','c7b6','b6c6','c6b5','d4b4','b5a6']
def pref_luc(b, acc):
    for u in LUC:
        if u in acc: return u
def pref_phil(b, acc):
    pawns=list(b.pieces(chess.PAWN, chess.WHITE))
    if not pawns: return None
    pr=chess.square_rank(pawns[0])
    for u in acc:
        m=chess.Move.from_uci(u)
        if b.piece_type_at(m.from_square)==chess.ROOK:
            tr=chess.square_rank(m.to_square)
            if pr<=4 and tr==5: return u
            if pr>=5 and tr<=1: return u
PREF={'lucena':pref_luc,'philidor':pref_phil}
S=json.load(open('study.json'))
S['endings']=[e for e in S['endings'] if not e['id'].startswith('lucena')]
L=[
 ('lucena','Rook endings','Lucena: build a bridge','1K6/1P2k3/8/8/8/8/r7/3R4 w - - 0 1','win',4,
  "The Lucena position is the most important winning rook ending. Your rook already cuts their king off. Lift it to the 4th rank (Rd4). When the side checks come, your king walks out toward the rook and the rook blocks the last check: that's the bridge."),
 ('philidor','Rook endings','Philidor: hold the draw','3k4/7R/r7/3PK3/8/8/8/8 b - - 0 1','draw',5,
  "The Philidor defence: keep your rook on your 3rd rank (here the 6th) so their king can't come forward. The moment the pawn steps onto that rank, swing the rook behind the king and check from far away: the king has nowhere to hide."),
 ('qvp','Queen vs pawn','Queen vs pawn on the 7th','K7/8/8/8/8/8/3kp3/7Q w - - 0 1','win',6,
  "Against a centre or knight pawn on the 7th, use checks and pins to force their king in front of its own pawn. Every time it blocks the pawn, you get a free move to bring your king one step closer. Then win the pawn."),

]
for id_,grp,name,fen,goal,n,why in L:
    b=chess.Board(fen); e0=ev(b,b.turn,24); print(id_, 'eval', e0)
    st=study(fen,goal,n,prefer=PREF.get(id_))
    print(id_, [ (s['play'], len(s['acc'])) for s in st])
    mv=[]; 
    for s in st: mv.append(s['play']); 
    S['endings'].append(dict(id='st-'+id_, group=grp, name=name, fen=fen, side='w' if b.turn else 'b', goal=goal, steps=st, why=why))
json.dump(S, open('study.json','w'), separators=(',',':'))
eng.quit()
