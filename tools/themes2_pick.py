import zstandard, io, csv, random, json, collections
WANT = {'smotheredMate':120,'anastasiaMate':120,'arabianMate':120,'bodenMate':80,'doubleBishopMate':100,'hookMate':100,'dovetailMate':100,'mateIn3':150,
        'deflection':150,'attraction':150,'clearance':120,'interference':100,'xRayAttack':100,'trappedPiece':150,'quietMove':150,'intermezzo':150,'doubleCheck':120,
        'zugzwang':100,'rookEndgame':150,'pawnEndgame':150,'exposedKing':120,'kingsideAttack':120}
random.seed(5)
res = collections.defaultdict(list); seen=set(); n=0
dctx = zstandard.ZstdDecompressor()
with open('puz.csv.zst','rb') as fh, dctx.stream_reader(fh) as r:
    tr = io.TextIOWrapper(r, encoding='utf-8')
    rd = csv.reader(tr); hdr = next(rd)
    I = {k:i for i,k in enumerate(hdr)}
    for row in rd:
        n+=1
        try: rating=int(row[I['Rating']]); pop=int(row[I['Popularity']]); plays=int(row[I['NbPlays']]); dev=int(row[I['RatingDeviation']])
        except: continue
        if not (600<=rating<=2000) or pop<85 or plays<300 or dev>90: continue
        th=row[I['Themes']].split()
        for t in th:
            if t in WANT and len(res[t]) < WANT[t]*6:
                res[t].append([row[I['PuzzleId']], row[I['FEN']], row[I['Moves']], rating])
                break
print('rows', n, {k:len(v) for k,v in res.items()})
out={}
for t,lst in res.items():
    # spread across ratings: bucket by 100, round-robin
    b=collections.defaultdict(list)
    for x in lst: b[x[3]//100].append(x)
    for v in b.values(): random.shuffle(v)
    pick=[]; keys=sorted(b)
    while len(pick)<WANT[t] and any(b[k] for k in keys):
        for k in keys:
            if b[k] and len(pick)<WANT[t]: pick.append(b[k].pop())
    out[t]=sorted(pick, key=lambda x:x[3])
json.dump(out, open('extra.json','w'), separators=(',',':'))
print({k:(len(v), v[0][3], v[-1][3]) for k,v in out.items()})
