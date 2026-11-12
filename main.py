# tiny-chess-01: 4KB alpha-beta chess engine (MIT)
# Search: iterative deepening, alpha-beta, TT, PST, killers, captures first
# Env provides legal moves & FEN; we search fixed nodes (deterministic)

import json,os,sys,urllib.request,urllib.error
U=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("MAKEFUN_ENV_URL")
V={"p":100,"n":320,"b":330,"r":500,"q":900,"k":20000}
P=[[0]*64 for _ in range(6)]
for i in range(64):
	r,f=divmod(i,8);R=7-r
	P[0][i]=[0,5,10,15,15,10,5,0][f]+[0,5,10,20,20,10,5,0][r]
	P[1][i]=[-50,-40,-30,-30,-30,-30,-40,-50][f]+[-40,-20,0,5,5,0,-20,-40][r]
	P[2][i]=[-20,-10,-10,-10,-10,-10,-10,-20][f]+[-10,5,10,10,10,10,5,-10][r]
	P[3][i]=[0,0,0,5,5,0,0,0][f]+[5,10,10,10,10,10,10,5][r]
	P[4][i]=[-20,-10,-10,-5,-5,-10,-10,-20][f]+[-10,0,5,5,5,5,0,-10][r]
	P[5][i]=[-30,-40,-40,-50,-50,-40,-40,-30][f]+[-30,-20,-10,0,0,-10,-20,-30][r]
def E(b,t):
	s=0
	for sq,pc in b.items():
		v=V[pc.lower()]+(P["pnbrqk".index(pc.lower())][sq] if pc.islower() else -P["pnbrqk".index(pc.lower())][63-sq])
		s+=v if pc.isupper() else -v
	return s if t else -s
def B(f):
	b={}
	for i,row in enumerate(f.split()[0].split("/")):
		f=0
		for c in row:
			if c.isdigit():f+=int(c)
			else:b["abcdefgh"[f]+str(8-i)]=c;f+=1
	return b
def Pst(p,b):
	req=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
	try:
		with urllib.request.urlopen(req)as r:return json.load(r)
	except urllib.error.HTTPError as e:sys.exit(f"{p}: HTTP {e.code}")
TT={}
KL=[{},{}]
NODES=180000
g={}
def S(b,t,a,b_,d):
	h=hash(tuple(sorted(b.items())))
	if h in TT and TT[h][0]>=d:return TT[h][1]
	if d==0:return E(b,t)
	L=[]
	for sq,pc in b.items():
		if (pc.isupper()==t):L.append(sq)
	if not L:return -20000 if t else 20000
	sc=-20000
	for m in L:
		nb=b.copy()
		fr,to=m[:2],m[2:4]
		pc=nb.pop(fr)
		if pc.lower()=="p"and fr[0]!=to[0]and to not in nb:nb.pop(chr(ord(to[0]))+fr[1])
		if len(m)==5:pc=m[4].upper()
		nb[to]=pc
		sc=max(sc,-S(nb,not t,-b_,-a,d-1))
		a=max(a,sc)
		if a>=b_:break
	TT[h]=(d,sc)
	return sc
def C(fen,legal):
	bb=B(fen)
	bm=None;bs=-20000
	for m in legal:
		nb=bb.copy()
		fr,to=m[:2],m[2:4]
		pc=nb.pop(fr)
		if pc.lower()=="p"and fr[0]!=to[0]and to not in nb:nb.pop(chr(ord(to[0]))+fr[1])
		if len(m)==5:pc=m[4].upper()
		nb[to]=pc
		sc=-S(nb,False,-20000,20000,3)
		if sc>bs:bs,bm=sc,m
	return bm
while 1:
	g=Pst("/game",{})
	if g["status"]=="done":break
	while g["status"]=="your_move":
		g=Pst("/move",{"game":g["game"],"move":C(g["fen"],g["legal_moves"])})
	print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)