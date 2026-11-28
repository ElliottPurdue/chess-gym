import json, random, chess, chess.engine
eng=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish'); eng.configure({'Threads':2,'Hash':256})
def score(b, me, d=22):
    return eng.analyse(b, chess.engine.Limit(depth=d))['score'].pov(me)
def solve_mate(fen, depth=26):
    """Return steps: for each of my moves, the accepted moves (keep forced mate within the remaining count), plus the defender reply."""
    b=chess.Board(fen); me=b.turn
    info=eng.analyse(b, chess.engine.Limit(depth=depth)); s=info['score'].pov(me)
    assert s.is_mate() and s.mate()>0, (fen, s)
    n=s.mate(); steps=[]
    for k in range(n):
        ms=list(b.legal_moves); acc=[]
        for m in ms:
            b2=b.copy(); b2.push(m)
            if b2.is_checkmate(): acc.append(m.uci()); continue
            sc=eng.analyse(b2, chess.engine.Limit(depth=18))['score'].pov(me)
            if sc.is_mate() and sc.mate()>0 and sc.mate()<=n-k-1: acc.append(m.uci())
        pvm=eng.analyse(b, chess.engine.Limit(depth=depth))['pv'][0]
        assert pvm.uci() in acc, (fen,k)
        b.push(pvm); reply=None
        if not b.is_game_over():
            reply=eng.analyse(b, chess.engine.Limit(depth=depth))['pv'][0]; 
        steps.append(dict(acc=acc, play=pvm.uci(), reply=reply.uci() if reply else None))
        if reply: b.push(reply)
    return n, steps
MATES=[
("back-rank","Back-rank mate","6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1","Black's own pawns box the king in. A rook or queen on the back rank finishes it. In your games: always give your king a flight square (h3 or h6) once the back rank gets dangerous."),
("smothered","Smothered mate","r6k/6pp/8/6N1/8/1Q6/6PP/6K1 w - - 0 1","Knight checks, double check, then the queen sacrifice on g8 forces the rook to block the king's last square. The knight mates a king trapped by its own pieces."),
("anastasia","Anastasia's mate","8/4N1pk/8/8/8/4R3/6PP/6K1 w - - 0 1","The knight on e7 covers g8 and g6. The rook swings to the h-file and the king has nowhere to go."),
("arabian","Arabian mate","7k/1R6/5N2/8/8/8/8/6K1 w - - 0 1","Rook and knight together: the knight guards the rook and covers g8, the rook checks from h7."),
("boden","Boden's mate","2kr4/p2n4/2p5/8/5B2/8/8/4KB2 w - - 0 1","Two bishops on crossing diagonals mate a king castled long. One covers b8 and c7, the other checks from a6."),
("damiano","Damiano's mate","5rk1/5p2/6P1/8/8/8/8/6KQ w - - 0 1","A pawn on g6 supports the queen on h7. Watch for this whenever a pawn reaches the sixth rank next to the king."),
("epaulette","Epaulette mate","3rkr2/8/8/8/8/8/Q7/6K1 w - - 0 1","The king's own rooks sit on its shoulders like epaulettes, so a queen check from e6 is mate: d7, e7 and f7 are all covered."),
("opera","Opera mate","4kb2/5p2/8/6B1/8/8/8/3RK3 w - - 0 1","Morphy's finish: the rook mates on d8 while the bishop guards it and covers e7."),
("legal","Légal's trap","rn1qkbnr/ppp2p1p/3p2p1/4p3/2B1P1b1/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 5","Black pinned your knight with ...Bg4, but the pin is fake: Nxe5! and if ...Bxd1, Bxf7+ and Nd5 is mate. If Black doesn't take the queen, you're simply a pawn up."),
]
out={'mates':[], 'endings':[]}
for id_,name,fen,why in MATES:
    b=chess.Board(fen)
    if id_=='legal':
        infos=eng.analyse(b, chess.engine.Limit(depth=24), multipv=3)
        s=[i['score'].pov(b.turn).score(mate_score=3000) for i in infos]; best=infos[0]['pv'][0]
        print(id_, [ (b.san(i['pv'][0]), sc) for i,sc in zip(infos,s)])
        out['mates'].append(dict(id='pat-'+id_, name=name, fen=fen, mate=None, steps=[dict(acc=[i['pv'][0].uci() for i,sc in zip(infos,s) if sc>=s[0]-60], play=best.uci(), reply=None)], why=why, line=b.variation_san(infos[0]['pv'][:7])))
        continue
    n,steps=solve_mate(fen)
    print(id_, 'mate in', n, [len(x['acc']) for x in steps], chess.Board(fen).variation_san([chess.Move.from_uci(x) for st in steps for x in [st['play']]+([st['reply']] if st['reply'] else [])]))
    out['mates'].append(dict(id='pat-'+id_, name=name, fen=fen, mate=n, steps=steps, why=why))
# ---------- King and pawn: unique winning / drawing moves (Stockfish has an exact KPK bitbase) ----------
random.seed(7)
def rnd_kpk():
    while True:
        b=chess.Board(None)
        wk=random.randrange(64); bk=random.randrange(64); f=random.randint(1,6); r=random.randint(2,5); p=chess.square(f,r-1)
        if len({wk,bk,p})<3 or chess.square_distance(wk,bk)<2: continue
        b.set_piece_at(wk,chess.Piece(chess.KING,True)); b.set_piece_at(bk,chess.Piece(chess.KING,False)); b.set_piece_at(p,chess.Piece(chess.PAWN,True))
        b.turn=random.choice([True,False])
        if b.is_valid() and not b.is_check() and not b.is_game_over(): return b
wins=[]; draws=[]; seen=set(); tries=0
while (len(wins)<14 or len(draws)<10) and tries<4000:
    tries+=1; b=rnd_kpk(); key=b.board_fen()+str(b.turn)
    if key in seen: continue
    seen.add(key)
    ms=list(b.legal_moves)
    if len(ms)<3: continue
    me=b.turn; vals=[]
    for m in ms:
        b2=b.copy(); b2.push(m)
        if b2.is_game_over(): v=0 if not b2.is_checkmate() else 3000
        else: v=eng.analyse(b2, chess.engine.Limit(depth=14))['score'].pov(me).score(mate_score=3000)
        vals.append((v,m))
    vals.sort(key=lambda x:-x[0])
    if me==chess.WHITE and len(wins)<14 and vals[0][0]>=900 and vals[1][0]<=100:
        wins.append((b.fen(), vals[0][1].uci(), b.san(vals[0][1])))
    if me==chess.BLACK and len(draws)<10 and vals[0][0]>=-60 and vals[1][0]<=-900:
        draws.append((b.fen(), vals[0][1].uci(), b.san(vals[0][1])))
print('kpk wins', len(wins), 'draws', len(draws), 'tries', tries)
for fen,u,san in wins: out['endings'].append(dict(id='kpk-w-'+fen.split(' ')[0].replace('/','_'), group='King and pawn', name='Win the pawn ending', fen=fen, side='w', accepted=[u], best=u, bestSan=san,
    why="Only one move wins. Think opposition and key squares: your king belongs in front of the pawn, two squares ahead if you can, and you want the opponent to be the one who has to move away."))
for fen,u,san in draws: out['endings'].append(dict(id='kpk-d-'+fen.split(' ')[0].replace('/','_'), group='King and pawn', name='Save the pawn ending', fen=fen, side='b', accepted=[u], best=u, bestSan=san,
    why="Only one move draws. Head for the square in front of the pawn, and take the opposition when the kings face each other: the side that must move away loses ground."))
# ---------- Lucena (rook ending) ----------
for fen,name,why in [("1K6/1P1k4/8/8/8/8/r7/2R5 w - - 0 1","Lucena: build a bridge","Check the king away first (Rd1+), then put your rook on the 4th rank (Rd4). When the checks come, your king walks out and the rook blocks the last check: the bridge.")]:
    b=chess.Board(fen); infos=eng.analyse(b, chess.engine.Limit(depth=28), multipv=4)
    s=[i['score'].pov(b.turn).score(mate_score=3000) for i in infos]
    print('lucena', [(b.san(i['pv'][0]),sc) for i,sc in zip(infos,s)], b.variation_san(infos[0]['pv'][:9]))
    acc=[i['pv'][0].uci() for i,sc in zip(infos,s) if sc>=s[0]-80 and sc>=500]
    out['endings'].append(dict(id='lucena-1', group='Rook endings', name=name, fen=fen, side='w', accepted=acc, best=infos[0]['pv'][0].uci(), bestSan=b.san(infos[0]['pv'][0]), why=why, line=b.variation_san(infos[0]['pv'][:9])))
eng.quit()
json.dump(out, open('/home/claude/study/study.json','w'), indent=0)
print('mates', len(out['mates']), 'endings', len(out['endings']))
