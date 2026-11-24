#!/usr/bin/env python3
"""PIXEL FIGHT estilo M.U.G.E.N | 24 lutadores, 12 mapas | pip install pygame | python pixel_fight.py
P1: A D W + F(soco) G(chute) H(especial) T(super)   P2: setas + J K L I   (1 jogador: os dois conjuntos valem)
Defesa: segure para TRAS. Super: barra azul cheia. F11 tela cheia, ESC volta."""
import pygame as pg, random, math, sys, array

W, H, GY = 320, 180, 150
K = lambda s: tuple(int(c, 16) * 17 for c in s)
sg = lambda v: 1 if v >= 0 else -1
cl = lambda v, a, b: max(a, min(b, v))

# ---------------- DADOS: GOLPES ----------------
KN = dict(fire='Bola de Fogo', freeze='Gelo', wave='Onda de Fogo', boom='Bumerangue', beam='Raio', dash='Investida',
          up='Golpe Ascendente', tele='Teleporte', spin='Redemoinho', mine='Mina', heal='Meditação', shield='Escudo',
          rush='Rajada', slam='Esmagar', rage='Fúria', grab='Agarrão', meteor='Meteoros', timestop='Tempo Parado',
          inferno='Inferno', chaos='Caos')
DUR = dict(fire=26, freeze=26, wave=34, boom=28, beam=34, dash=30, up=34, tele=26, spin=38, mine=22, heal=62, shield=70,
           rush=50, slam=60, rage=30, grab=30, meteor=50, timestop=40, inferno=40)
AD = dict(fire=1, freeze=90, wave=1, boom=0, beam=0, dash=4.5, up=0, tele=0, spin=0, mine=0, heal=12, shield=0, rush=8,
          slam=0, rage=0, grab=0, meteor=5, timestop=90, inferno=0)
CLOSE = ('grab', 'spin', 'rush', 'up', 'slam', 'tele')
PN = dict(dj='Pulo duplo', regen='Regenera', dr='Armadura', ls='Rouba vida', mg='Energia rápida')


def ch(n, b, a, h, s, lk, hp, sp, jm, pu, ki, spc, cd, sup, bw=0, **pas):
    return dict(n=n, b=K(b), a=K(a), h=K(h), s=K(s), lk=lk, hp=hp, spd=sp, jm=jm, pu=pu, ki=ki,
                sp=spc[:3] + (K(spc[3]),), cd=cd, su=sup[:3] + (K(sup[3]),), bw=bw, pas=pas)


# nome, corpo, detalhe, cabelo, pele, visual(0 faixa,1 espetado,2 elmo,3 capuz,4 chifres), vida, vel, pulo, soco, chute,
# especial(tipo,dano,arg,cor), recarga, super(tipo,dano,arg,cor), largura, passivas
CH = [
    ch('KAZE', 'eee', 'e33', '321', 'fb7', 0, 100, 1.4, 5.6, 6, 9, ('fire', 9, 1, 'f82'), 70, ('beam', 32, 0, 'f44')),
    ch('TORA', 'd82', '420', '111', 'c85', 1, 115, 1.3, 5.3, 7, 10, ('dash', 14, 4.5, 'fa0'), 80, ('rush', 5, 10, 'fa0'), 2, dr=.12),
    ch('YUKI', '8cf', 'fff', 'ccf', 'fdc', 2, 90, 1.5, 5.8, 5, 8, ('freeze', 7, 120, '8ef'), 90, ('timestop', 0, 150, '8ef')),
    ch('BRUNO', '555', 'c33', '000', 'e96', 4, 140, 1.0, 5, 9, 12, ('grab', 22, 0, 'fff'), 100, ('slam', 34, 0, 'fc3'), 4, dr=.1),
    ch('LUNA', '63a', 'fe8', 'a8f', 'fdc', 0, 90, 1.5, 5.8, 5, 8, ('tele', 13, 0, 'c8f'), 80, ('meteor', 12, 6, 'c8f'), 0, dj=1),
    ch('ZEN', 'fa3', 'fff', 'd96', 'd96', 0, 105, 1.3, 5.5, 5, 8, ('heal', 18, 0, '8f8'), 220, ('beam', 26, 1, '8f8'), 0, regen=1),
    ch('SABRE', '2a8', 'ccc', '222', 'eb8', 1, 95, 1.8, 6, 5, 8, ('spin', 4, 0, 'fff'), 100, ('rush', 6, 12, '8ff')),
    ch('GOLEM', '987', '653', '987', '987', 2, 150, .9, 4.8, 10, 13, ('shield', 0, 0, '8cf'), 160, ('slam', 38, 0, 'a86'), 4, dr=.15),
    ch('VIPER', '383', 'ad2', '131', 'cd8', 3, 95, 1.5, 5.8, 5, 8, ('mine', 20, 0, 'af0'), 110, ('beam', 30, 1, 'af0'), 0, ls=.12),
    ch('HANA', 'f8b', 'fff', 'a24', 'fdc', 0, 92, 1.6, 6, 5, 8, ('boom', 10, 0, 'f6a'), 80, ('rush', 5, 14, 'f6a'), 0, dj=1),
    ch('ONI', 'c22', 'fe6', '000', 'e55', 4, 125, 1.3, 5.4, 8, 11, ('rage', 0, 0, 'f44'), 300, ('inferno', 26, 0, 'f60'), 2, ls=.1),
    ch('NOVA', '49f', '4ff', '124', 'fcb', 1, 95, 1.5, 5.8, 5, 8, ('beam', 20, 0, '4ff'), 100, ('meteor', 14, 8, '4ff'), 0, mg=1.6),
    ch('DRAKO', '931', 'f90', '510', 'b74', 4, 110, 1.2, 5.4, 7, 10, ('wave', 16, 1, 'f70'), 110, ('inferno', 30, 0, 'f50'), 2, dr=.08),
    ch('MIKA', 'fd3', 'f63', '730', 'fb8', 0, 90, 1.8, 6.2, 5, 8, ('rush', 3, 8, 'ff6'), 90, ('timestop', 0, 120, 'ff6')),
    ch('TITAN', '36c', 'fc3', '420', 'e96', 2, 145, 1.0, 5, 9, 12, ('slam', 16, 0, 'fc3'), 110, ('grab', 42, 0, 'fff'), 4),
    ch('SHADE', '224', '808', '000', '988', 3, 92, 1.6, 5.8, 5, 8, ('tele', 15, 0, 'a4f'), 70, ('beam', 30, 1, 'a4f'), 0, ls=.1),
    ch('BOLT', 'ee3', '38f', '38f', 'fc9', 1, 85, 2.0, 6.2, 5, 8, ('dash', 11, 6.5, 'ff4'), 60, ('rush', 5, 16, 'ff4')),
    ch('FROST', '5ad', 'fff', 'fff', 'cef', 2, 100, 1.3, 5.5, 6, 9, ('freeze', 9, 150, 'bff'), 100, ('inferno', 24, 0, '8ef')),
    ch('SPECTER', 'bbd', '88f', 'fff', 'dde', 3, 90, 1.5, 5.8, 5, 8, ('boom', 12, 0, 'aaf'), 70, ('meteor', 13, 7, 'aaf'), 0, dj=1),
    ch('AMAZONA', 'a52', 'fd0', '310', 'c84', 0, 108, 1.5, 6, 6, 9, ('up', 15, 0, 'fd0'), 80, ('rush', 6, 12, 'fd0'), 0, dj=1),
    ch('MONGE', 'f93', '630', 'd96', 'd96', 0, 105, 1.3, 5.5, 5, 8, ('shield', 0, 1, 'fc6'), 150, ('beam', 28, 0, 'fc6'), 0, regen=1),
    ch('BUFÃO', 'a3c', '3d8', 'f3a', 'fec', 1, 98, 1.5, 5.8, 5, 8, ('chaos', 10, 0, 'f8f'), 80, ('meteor', 11, 7, 'f8f'), 0, mg=1.4),
    ch('CYBER', '666', '0ef', '0ef', 'abb', 2, 110, 1.3, 5.5, 6, 9, ('fire', 6, 3, '0ef'), 90, ('rush', 7, 12, '0ef'), 2, dr=.1),
    ch('CAVALEIRO', 'aab', 'c33', '777', 'eb9', 2, 120, 1.1, 5.2, 8, 11, ('up', 17, 0, 'ddd'), 90, ('slam', 34, 0, 'ddd'), 2, dr=.12),
]


# ---------------- DADOS: MAPAS ----------------
def mp(n, sky, layers, fl, orb=None, st=0, **k):
    return dict(n=n, sky=[K(c) for c in sky], layers=[(K(c), b, a, f, p, t) for c, b, a, f, p, t in layers],
                fl=[K(c) for c in fl], orb=orb and (orb[0], orb[1], orb[2], K(orb[3])), st=st, **k)


MAPS = [
    mp('Dojo ao Entardecer', ['236', '537', 'a47', 'e56', 'f85', 'fb6', 'fd8'], [('425', 50, 22, .03, 0, 'hill'), ('213', 34, 16, .045, 2, 'hill')], ['863', '542', '431'], (160, 96, 26, 'ffd')),
    mp('Cidade Neon', ['102', '204', '326', '538'], [('415', 70, 40, 0, 3, 'city'), ('206', 45, 30, 0, 7, 'city')], ['333', '222', 'f0f'], (250, 40, 14, 'fef'), 40),
    mp('Floresta Sombria', ['134', '245', '366', '4a7'], [('142', 60, 30, 0, 0, 'pine'), ('021', 40, 26, 0, 1, 'pine')], ['542', '321', '210'], (240, 36, 12, 'dfd'), 20),
    mp('Deserto', ['fc6', 'fd8', 'fe9', 'ffb'], [('ea5', 36, 20, .02, 0, 'hill'), ('d94', 22, 14, .035, 3, 'hill')], ['eb7', 'ca5', 'b94'], (80, 50, 24, 'fff')),
    mp('Vulcão', ['200', '400', '610', '820'], [('310', 70, 40, .1, 1, 'spike'), ('200', 45, 30, .12, 3, 'spike')], ['f60', 'a30', '511'], (160, 60, 20, 'f94')),
    mp('Montanha Gelada (escorrega)', ['8be', '9cf', 'bdf', 'def'], [('cde', 70, 30, .1, 0, 'spike'), ('9bd', 40, 20, 0, 2, 'pine')], ['eff', 'bde', '9bc'], ice=True),
    mp('Ruínas Antigas', ['356', '467', '589', '7ab'], [('678', 60, 36, 0, 5, 'city'), ('456', 36, 22, 0, 9, 'city')], ['998', '776', '554'], (60, 40, 16, 'ffe')),
    mp('Porto Noturno', ['012', '023', '135', '247'], [('124', 50, 26, 0, 2, 'city'), ('013', 30, 14, .03, 0, 'hill')], ['864', '531', '421'], (260, 36, 14, 'eef'), 70),
    mp('Espaço (gravidade baixa)', ['000', '102', '204'], [], ['557', '335', '88f'], (230, 70, 34, 'a5f'), 120, g=.2),
    mp('Pântano', ['564', '675', '786', '897'], [('231', 55, 30, 0, 0, 'pine'), ('120', 35, 22, 0, 2, 'pine')], ['563', '342', '231']),
    mp('Coliseu', ['6af', '8cf', 'aef', 'cff'], [('dc9', 70, 30, 0, 4, 'city'), ('ba7', 44, 22, 0, 1, 'city')], ['eb8', 'ca6', 'b95'], (270, 30, 18, 'ff9')),
    mp('Castelo Assombrado', ['113', '225', '437', '648'], [('324', 80, 30, .08, 0, 'spike'), ('213', 45, 26, .06, 2, 'hill')], ['889', '667', '445'], (70, 38, 16, 'ffd'), 50),
]


def make_map(m):
    s = pg.Surface((W, H)); n = len(m['sky']); r = random.Random(len(m['n']))
    for i, c in enumerate(m['sky']): s.fill(c, (0, i * GY // n, W, GY // n + 2))
    for _ in range(m['st']): s.set_at((r.randrange(W), r.randrange(100)), (255, 255, 255))
    if m['orb']: x, y, rad, c = m['orb']; pg.draw.circle(s, c, (x, y), rad)
    for c, b, a, f, p, t in m['layers']:
        for x in range(0, W, 2):
            if t == 'city': h = b + ((x // 14) * 73 + p * 11) % a
            elif t == 'pine': h = b + a * (1 - abs(((x / (10 + p * 3)) % 1) * 2 - 1))
            elif t == 'spike': h = b + a * abs(math.sin(x * f + p))
            else: h = b + a * math.sin(x * f + p) + a * .4 * math.sin(x * f * 3.1 + p)
            s.fill(c, (x, GY - int(h), 2, int(h)))
    top, mid, ln = m['fl']
    s.fill(mid, (0, GY, W, H - GY)); s.fill(top, (0, GY, W, 2))
    for x in range(0, W, 16): s.fill(ln, (x, GY + 2, 1, H - GY))
    s.fill(ln, (0, GY + 14, W, 1))
    return s


# ---------------- ESTADO GLOBAL ----------------
X = {}; P = []; PJ = []; MN = []; PT = []; SF = []; SN = {}; FT = {}
HL = [{}, {}]; PR = [{}, {}]
NO = dict(l=0, r=0, u=0, punch=0, kick=0, sp=0, su=0, uj=0)
ATK = dict(punch=dict(dur=14, a=4, b=8, rng=20, kb=2, k='pu'), kick=dict(dur=22, a=7, b=12, rng=27, kb=3.5, k='ki'))


def snd(n):
    if n in SN: SN[n].play()


def mk_snd(f, d, v=.15):
    n = int(22050 * d)
    b = array.array('h', [int(v * 32767 * (1 if (i * f / 22050) % 1 < .5 else -1) * (1 - i / n)) for i in range(n)])
    return pg.mixer.Sound(buffer=b.tobytes())


def spark(x, y, c, n=8):
    if isinstance(c, str): c = K(c)
    for _ in range(n):
        a = random.random() * 6.28; s = 1 + random.random() * 2
        PT.append([x, y, math.cos(a) * s, math.sin(a) * s - .5, 12 + random.randrange(8), c])


class F:
    def __init__(s, d, x, face, pi):
        s.d = d; s.pi = pi; s.x = x; s.y = GY; s.vx = s.vy = 0; s.face = face; s.hp = s.dhp = d['hp']
        s.st = 'idle'; s.t = s.tm = 0; s.ground = True; s.blk = False; s.meter = 0; s.cd = 0; s.inv = 0
        s.buff = s.slow = s.frz = s.shield = s.reflect = 0; s.sp = None; s.done = False
        s.dj = d['pas'].get('dj', 0); s.dur = 0


# ---------------- COMBATE ----------------
def hit(a, o, dmg, kb, sx, unb=False):
    if o.st == 'ko' or o.inv > 0: return False
    if a.buff: dmg *= 1.4
    d = sg(o.x - sx); px, py = o.x, o.y - 22
    if o.blk and o.st == 'idle' and not unb and o.face == -d:
        o.hp -= dmg * .12; o.vx = d * kb * .5; o.meter = min(100, o.meter + 2)
        spark(px - d * 4, py, '6cf', 5); snd('blk'); return True
    if o.shield and not unb:
        o.hp -= dmg * .2; o.vx = d * .5; spark(px, py, '8cf', 5); snd('blk'); return True
    dmg *= 1 - o.d['pas'].get('dr', 0)
    o.hp -= dmg; o.st = 'hit'; o.tm = 12 + (8 if dmg > 12 else 0); o.vx = d * kb; o.sp = None; o.blk = False
    if not o.ground: o.vy = -2
    a.meter = min(100, a.meter + dmg * 1.2 * a.d['pas'].get('mg', 1)); o.meter = min(100, o.meter + dmg * .7)
    a.hp = min(a.d['hp'], a.hp + dmg * a.d['pas'].get('ls', 0))
    spark(px, py, 'fff', 8); X['shake'] = 6 if dmg > 12 else 3; X['stop'] = 3; snd('hit')
    if o.hp <= 0: o.hp = 0; o.st = 'ko'; o.vx = d * 3; o.vy = -4; o.ground = False; snd('ko')
    return True


def near(f, o, rng, vert=34):
    dx = (o.x - f.x) * f.face
    return -6 < dx < rng and abs(f.y - o.y) < vert


def proj(o, x, y, vx, vy, dm, c, w=6, h=6, life=120, **kw):
    PJ.append(dict(o=o, x=x, y=y, vx=vx, vy=vy, dm=dm, c=c, w=w, h=h, life=life, t=0, used=False, **kw))


def upd_proj():
    for p in PJ[:]:
        p['t'] += 1; p['life'] -= 1; p['x'] += p['vx']; p['y'] += p['vy']
        if p.get('bm') and p['t'] == 36: p['vx'] *= -1; p['used'] = False
        tg = P[1 - p['o'].pi]
        r = pg.Rect(int(p['x'] - p['w'] / 2), int(p['y'] - p['h'] / 2), int(p['w']), int(p['h']))
        if not p['used'] and r.colliderect(pg.Rect(int(tg.x - 6), int(tg.y - 38), 12, 38)):
            if tg.reflect > 0 and p['vx'] and not p.get('beam'):
                p['o'] = tg; p['vx'] *= -1; continue
            dn = sg(p['vx']) if p['vx'] else p['o'].face
            if hit(p['o'], tg, p['dm'], p.get('kb', 2.5), tg.x - dn * 10):
                p['used'] = True
                if p.get('slow'): tg.slow = p['slow']
                if p.get('drain'): p['o'].hp = min(p['o'].d['hp'], p['o'].hp + p['dm'] * .8)
                if not p.get('pierce'): PJ.remove(p); continue
        if p.get('fall') and p['y'] >= GY - 4: spark(p['x'], GY - 4, p['c'], 6); PJ.remove(p); continue
        if p['life'] <= 0 or p['x'] < -40 or p['x'] > W + 40: PJ.remove(p)


def upd_mines():
    for m in MN[:]:
        m['life'] -= 1; tg = P[1 - m['o'].pi]
        if m['life'] <= 0: MN.remove(m)
        elif tg.ground and abs(tg.x - m['x']) < 9 and tg.st != 'ko':
            hit(m['o'], tg, m['dm'], 4, m['x'], True); tg.vy = -3; tg.ground = False
            spark(m['x'], GY - 4, m['c'], 14); X['shake'] = 5; MN.remove(m)


def start(f, s, big):
    k = s[0]
    if k == 'chaos': k = random.choice(list(AD)); s = (k, s[1], AD[k], s[3])
    f.st = 'spec'; f.tm = 0; f.done = False; f.blk = False; f.sp = (s, big)
    f.dur = {'rush': 14 + int(s[2]) * 4, 'meteor': 14 + 6 * int(s[2])}.get(k, DUR[k])
    if big: f.inv = 18; X['shake'] = 4; spark(f.x, f.y - 20, s[3], 14)
    else: f.cd = f.d['cd']
    snd('spec')


def spec(f, o):
    (k, dm, ar, c), big = f.sp; f.tm += 1; t = f.tm; fd = f.face; y = f.y - 24
    if k in ('fire', 'freeze', 'wave', 'boom') and t == 10:
        n = int(ar) if k == 'fire' else 1
        for i in range(n):
            if k == 'wave': proj(f, f.x + fd * 12, GY - 12, fd * 1.8, 0, dm, c, 16, 24, 200, pierce=1)
            else: proj(f, f.x + fd * 12, y, fd * (3 if k == 'freeze' else 3.4), (i - (n - 1) / 2) * .6, dm, c, 7, 7, 140,
                       slow=ar if k == 'freeze' else 0, bm=(k == 'boom'))
    elif k == 'beam' and t == 12:
        x0 = f.x if fd > 0 else 0; L = W - f.x if fd > 0 else f.x
        proj(f, x0 + L / 2, y, 0, 0, dm, c, L, 14 if big else 8, 8, pierce=1, beam=1, drain=ar)
    elif k == 'dash':
        if 6 <= t <= 22:
            f.vx = fd * ar
            if not f.done and near(f, o, 16): f.done = True; hit(f, o, dm, 4, f.x); f.vx *= .3
        elif t > 22: f.vx *= .6
    elif k == 'up':
        if t == 2: f.inv = 14
        if t == 4: f.vy = -5.8; f.vx = fd * 1.2
        if 4 <= t <= 22 and not f.done and near(f, o, 18, 50):
            f.done = True
            if hit(f, o, dm, 3, f.x) and o.st == 'hit': o.vy = -4; o.ground = False
    elif k == 'tele':
        if t == 8:
            spark(f.x, f.y - 20, c, 10); f.x = cl(o.x + sg(o.x - f.x) * 20, 12, W - 12); f.face = sg(o.x - f.x); f.inv = 8
            spark(f.x, f.y - 20, c, 10)
        if t == 14 and near(f, o, 28): hit(f, o, dm, 3, f.x)
    elif k == 'spin':
        if 4 <= t <= 34:
            f.vx = fd * .9
            if t % 6 == 4 and abs(o.x - f.x) < 26 and abs(f.y - o.y) < 36: hit(f, o, dm, 1.5, f.x)
    elif k == 'mine' and t == 10:
        MN[:] = [m for m in MN if m['o'] is not f]; MN.append(dict(o=f, x=f.x, dm=dm, life=900, c=c))
    elif k == 'heal':
        if t % 6 == 0: f.hp = min(f.d['hp'], f.hp + dm / 10); spark(f.x, f.y - 30, c, 2)
    elif k == 'shield': f.shield = 2; f.reflect = 2 if ar else 0
    elif k == 'rush':
        if 6 <= t <= f.dur - 8 and t % 4 == 2:
            f.vx = fd * .9
            if near(f, o, 24): hit(f, o, dm, .8, f.x)
    elif k == 'slam':
        if t == 4: f.vy = -6.5; f.vx = fd * 1.8
        if t > 8 and f.ground and not f.done:
            f.done = True; f.vx = 0; X['shake'] = 7; f.tm = max(f.tm, f.dur - 18)
            if abs(o.x - f.x) < 30 and o.ground: hit(f, o, dm, 4, f.x)
            for s in (-1, 1): proj(f, f.x + s * 12, GY - 5, s * 2.6, 0, dm * .5, c, 10, 8, 40)
    elif k == 'rage' and t == 10: f.buff = 300; spark(f.x, f.y - 22, c, 16)
    elif k == 'grab' and t == 10:
        if abs(o.x - f.x) < 28 and o.ground and o.st != 'ko':
            hit(f, o, dm, 5, f.x, True); o.vy = -3; o.ground = False
    elif k == 'meteor':
        if t >= 2 and (t - 2) % 6 == 0 and (t - 2) // 6 < int(ar):
            proj(f, o.x + random.randint(-40, 40), -8, 0, 3.8, dm, c, 9, 14, 120, fall=1)
    elif k == 'timestop' and t == 10: o.frz = int(ar); spark(o.x, o.y - 20, c, 20); X['shake'] = 3
    elif k == 'inferno' and t == 12:
        for s in (-1, 1): proj(f, f.x + s * 10, GY - 14, s * 2.2, 0, dm, c, 18, 28, 160, pierce=1)
    if f.tm >= f.dur: f.st = 'idle'; f.sp = None; f.vx *= .5


def step(f, o, inp, m):
    f.t += 1; D = f.d; pas = D['pas']
    f.vy += m.get('g', .35); f.y += f.vy; f.x += f.vx
    if f.y >= GY:
        if not f.ground: f.dj = pas.get('dj', 0)
        f.y = GY; f.vy = 0; f.ground = True
    else: f.ground = False
    f.x = cl(f.x, 12, W - 12)
    for a in ('cd', 'inv', 'buff', 'slow', 'shield', 'reflect'):
        if getattr(f, a) > 0: setattr(f, a, getattr(f, a) - 1)
    f.dhp = f.dhp - .5 if f.dhp > f.hp else f.hp
    if f.st == 'ko': f.vx *= .9; return
    if pas.get('regen'): f.hp = min(D['hp'], f.hp + .03 * pas['regen'])
    if f.frz > 0: f.frz -= 1; f.vx = 0; return
    if f.st == 'hit':
        f.tm -= 1; f.vx *= .85
        if f.tm <= 0: f.st = 'idle'
        return
    if f.st in ATK:
        A = ATK[f.st]; f.tm += 1
        if f.ground: f.vx *= .6
        if not f.done and A['a'] <= f.tm <= A['b']:
            dx = (o.x - f.x) * f.face
            if 0 <= dx <= A['rng'] + 8 and abs(f.y - o.y) <= 30: f.done = True; hit(f, o, D[A['k']], A['kb'], f.x)
        if f.tm > A['dur']: f.st = 'idle'
        return
    if f.st == 'spec': spec(f, o); return
    sp = D['spd'] * (1.25 if f.buff else 1) * (.5 if f.slow else 1)
    d = inp['r'] - inp['l']; f.blk = False
    if f.ground:
        f.face = 1 if o.x > f.x else -1
        f.blk = d == -f.face
        tg = d * sp * (.55 if f.blk else 1 if d == f.face else .8)
        f.vx += (tg - f.vx) * (.07 if m.get('ice') else 1)
    elif d: f.vx = d * sp
    if inp['u'] and f.ground: f.vy = -D['jm']; f.ground = False
    elif inp['uj'] and not f.ground and f.dj > 0: f.dj -= 1; f.vy = -D['jm'] * .9; spark(f.x, f.y, 'fff', 4)
    if inp['su'] and f.meter >= 100: f.meter = 0; start(f, D['su'], True)
    elif inp['sp'] and f.cd <= 0: start(f, D['sp'], False)
    elif inp['punch'] or inp['kick']:
        f.st = 'punch' if inp['punch'] else 'kick'; f.tm = 0; f.done = False
        if f.ground: f.vx = f.face * .9
        snd('whoosh')


def ai(f, o, s):
    i = dict(NO); dist = abs(o.x - f.x); tw = sg(o.x - f.x); s['t'] -= 1
    if s['t'] <= 0:
        s['t'] = 8 + random.randrange(14)
        s['a'] = random.choice(['fwd', 'fwd', 'jump', 'spec'] if dist > 60 else ['fwd', 'punch', 'kick', 'spec'] if dist > 36
                               else ['punch', 'punch', 'kick', 'kick', 'back', 'spec'])
    if o.st in ('punch', 'kick', 'spec') and dist < 45 and random.random() < .05: s['a'] = 'back'; s['t'] = 16
    a = s['a']; k = f.d['sp'][0]
    mv = lambda v: i.__setitem__('r' if v > 0 else 'l', 1)
    if a == 'fwd': mv(tw)
    elif a == 'back': mv(-tw)
    elif a == 'jump': i['u'] = 1; mv(tw)
    elif a == 'punch':
        if dist < 30: i['punch'] = 1; s['a'] = 'fwd'; s['t'] = 12
        else: mv(tw)
    elif a == 'kick':
        if dist < 36: i['kick'] = 1; s['a'] = 'back'; s['t'] = 10
        else: mv(tw)
    elif a == 'spec':
        if f.cd <= 0 and (dist < 42 if k in CLOSE else dist > 44 or k in ('shield', 'rage', 'heal', 'mine')):
            i['sp'] = 1; s['a'] = 'back'; s['t'] = 14
        else: mv(tw); s['t'] = min(s['t'], 6)
    if f.meter >= 100 and random.random() < .02: i['su'] = 1
    return i


# ---------------- FLUXO ----------------
def press(p, k, dn):
    HL[p][k] = dn
    if dn and k in ('punch', 'kick', 'sp', 'su', 'u'): PR[p][k] = True


def inp_of(i):
    h = HL[i]; q = PR[i]
    o = dict(l=int(bool(h.get('l'))), r=int(bool(h.get('r'))), u=int(bool(h.get('u'))), punch=int(bool(q.get('punch'))),
             kick=int(bool(q.get('kick'))), sp=int(bool(q.get('sp'))), su=int(bool(q.get('su'))), uj=int(bool(q.get('u'))))
    q.clear(); return o


def new_round():
    X.update(scr='fight', st='intro', t=0, timer=60, tick=0, ai=dict(t=0, a='fwd'), ai0=dict(t=0, a='fwd'))
    P[:] = [F(CH[X['c'][0]], 100, 1, 0), F(CH[X['c'][1]], 220, -1, 1)]
    PJ.clear(); MN.clear(); PT.clear(); PR[0].clear(); PR[1].clear()


def end_round():
    a, b = P; w = 0 if a.hp > b.hp else 1 if b.hp > a.hp else -1
    if w >= 0: X['w'][w] += 1
    X['msg'] = 'EMPATE' if w < 0 else 'K.O.!' if min(a.hp, b.hp) <= 0 else 'TEMPO!'
    X['st'] = 'rend'; X['t'] = 0


def upd():
    m = MAPS[X['mi']]; X['shake'] = max(0, X['shake'] - 1)
    for q in PT[:]:
        q[0] += q[2]; q[1] += q[3]; q[3] += .15; q[4] -= 1
        if q[4] <= 0: PT.remove(q)
    X['t'] += 1; s = X['st']
    if s == 'intro':
        step(P[0], P[1], NO, m); step(P[1], P[0], NO, m); PR[0].clear(); PR[1].clear()
        if X['t'] > 100: X['st'] = 'fight'
    elif s == 'fight':
        if X['stop'] > 0: X['stop'] -= 1; return
        i0 = inp_of(0) if X['mode'] else ai(P[0], P[1], X['ai0'])
        i1 = inp_of(1) if X['mode'] == 2 else ai(P[1], P[0], X['ai'])
        step(P[0], P[1], i0, m); step(P[1], P[0], i1, m); upd_proj(); upd_mines()
        gap = P[1].x - P[0].x
        if abs(gap) < 12 and P[0].ground and P[1].ground:
            sh = (12 - abs(gap)) / 2 * sg(gap); P[0].x -= sh; P[1].x += sh
        X['tick'] += 1
        if X['tick'] % 60 == 0: X['timer'] -= 1
        if P[0].hp <= 0 or P[1].hp <= 0 or X['timer'] <= 0: end_round()
    elif s == 'rend':
        step(P[0], P[1], NO, m); step(P[1], P[0], NO, m); upd_proj()
        if X['t'] > 150:
            if max(X['w']) >= 2:
                w1 = X['w'][0] >= 2
                X['res'] = ('JOGADOR 1' if w1 else 'JOGADOR 2' if X['mode'] == 2 else 'CPU') + ' VENCEU!' if X['mode'] != 1 or not w1 else 'VOCÊ VENCEU!'
                X['scr'] = 'over'
            else: X['rd'] += 1; w = list(X['w']); new_round(); X['w'] = w


# ---------------- DESENHO ----------------
def T(S, t, x, y, c=(255, 255, 255), sz=1, al=0):
    f = FT.get(sz) or FT.setdefault(sz, pg.font.Font(None, {1: 13, 2: 24, 3: 40}[sz]))
    im = f.render(t, False, c); sh = f.render(t, False, (0, 0, 0))
    px = x - (im.get_width() // 2 if al == 1 else im.get_width() if al == 2 else 0)
    S.blit(sh, (px + 1, y + 1)); S.blit(im, (px, y))


def draw_f(S, f):
    d = f.face; D = f.d; gi, ac, hr, sk = D['b'], D['a'], D['h'], D['s']; pn = tuple(int(c * .75) for c in gi); bw = D['bw']

    def R(x, y, w, h, c): S.fill(c, (round(f.x + (x if d > 0 else -x - w)), round(f.y + y), w, h))
    S.fill((24, 14, 28), (round(f.x) - 9, GY, 18, 2))
    if f.st == 'hit' and (f.tm >> 1) & 1: gi = (255, 255, 255)
    if f.st == 'ko' and f.ground:
        R(-24, -9, 10, 9, sk); R(-24, -9, 10, 4, hr); R(-14, -10, 16, 10, gi); R(-14, -6, 16, 2, ac); R(2, -8, 16, 8, pn); R(18, -4, 4, 4, (34, 34, 34)); return
    hurt = f.st in ('hit', 'ko'); L = -3 if hurt else 0
    air = not f.ground; walk = not air and f.st == 'idle' and abs(f.vx) > .2; a = (2 if (f.t >> 3) & 1 else -2) if walk else 0
    bob = (f.t >> 4) & 1 if (not walk and not air and f.st == 'idle' and not f.blk) else 0
    sh = (34, 34, 34)
    if air: R(-6 + L, -12, 5, 9, pn); R(-7 + L, -3, 7, 3, sh)
    else: R(-7 + L - a, -14, 5, 14, pn); R(-8 + L - a, -2, 7, 2, sh)
    if f.st == 'kick': R(1, -20, 24, 5, pn); R(24, -22, 6, 8, sh)
    elif air: R(2 + L, -14, 5, 8, pn); R(1 + L, -6, 7, 3, sh)
    else: R(2 + L + a, -14, 5, 14, pn); R(1 + L + a, -2, 8, 2, sh)
    R(-6 + L - bw // 2, -28 + bob, 12 + bw, 14, gi); R(-6 + L - bw // 2, -16 + bob, 12 + bw, 2, ac)
    hx = -5 + L * 2; hy = -39 + bob
    R(hx, hy, 10, 10, sk); R(hx, hy, 10, 4, hr); R(1 + L * 2, hy + 3, 2, 2, (226, 34, 34) if hurt else (17, 17, 17))
    lk = D['lk']
    if lk == 0: R(hx, hy + 5, 10, 2, ac); R(hx - 4, hy + 5 + ((f.t >> 3) & 1), 4, 2, ac)
    elif lk == 1: R(hx, hy - 3, 3, 4, hr); R(hx + 4, hy - 5, 3, 6, hr); R(hx + 7, hy - 3, 3, 4, hr)
    elif lk == 2: R(hx - 1, hy - 1, 12, 6, ac); R(hx - 1, hy + 5, 2, 5, ac)
    elif lk == 3: R(hx - 1, hy - 1, 12, 7, hr); R(hx - 1, hy + 6, 3, 8, hr); R(hx + 6, hy + 7, 4, 3, hr)
    else: R(hx - 1, hy - 5, 2, 6, ac); R(hx + 8, hy - 5, 2, 6, ac)
    if f.st == 'punch': e = min(20, f.tm * 5); R(0, -27, e, 4, sk); R(e, -29, 6, 7, ac)
    elif f.st == 'spec':
        k = f.sp[0][0]
        if k == 'spin': R(-14, -27, 28, 4, ac if (f.t >> 1) & 1 else sk)
        elif k == 'up': R(2, -48, 5, 22, sk); R(1, -52, 7, 6, ac)
        elif k == 'shield': R(2, -37, 6, 17, ac)
        elif k in ('slam', 'rage'): R(-8, -32, 4, 8, ac); R(4, -32, 4, 8, ac)
        else: e = 14 + ((f.t >> 1) & 1) * 3; R(0, -27, e, 4, sk); R(e, -29, 6, 7, ac)
    elif f.blk: R(2, -37, 6, 17, ac); R(-1, -26, 4, 6, gi)
    elif hurt: R(-9, -25, 4, 9, sk); R(2, -24, 4, 9, sk)
    else: R(-9, -26 + bob, 5, 4, sk); R(1, -27 + bob, 6, 4, sk); R(7, -29 + bob, 5, 6, ac)
    if f.shield: pg.draw.ellipse(S, f.sp[0][3] if f.sp else ac, (round(f.x) - 15, round(f.y) - 52, 30, 54), 1)
    for j, (on, c) in enumerate(((f.buff, (255, 220, 40)), (f.slow, (110, 220, 255)), (f.frz, (255, 255, 255)))):
        if on: S.fill(c, (round(f.x) - 4 + j * 3, round(f.y) - 52, 3, 3))


def hud(S):
    for i, f in enumerate(P):
        r = i == 1; x = W - 132 if r else 12; w = 120; mx = f.d['hp']
        S.fill((0, 0, 0), (x - 2, 8, w + 4, 12)); dw = int(w * f.dhp / mx); hw = int(w * f.hp / mx)
        S.fill((255, 204, 51), (x + w - dw if r else x, 10, dw, 8))
        S.fill((51, 221, 51) if f.hp > mx * .3 else (238, 51, 51), (x + w - hw if r else x, 10, hw, 8))
        mw = int(w * f.meter / 100); S.fill((0, 0, 0), (x - 2, 22, w + 4, 7))
        S.fill((60, 160, 255) if f.meter < 100 else (255, 240, 80), (x + w - mw if r else x, 23, mw, 5))
        cw = int(w * (1 - f.cd / f.d['cd'])); S.fill((60, 220, 120) if f.cd <= 0 else (90, 90, 90), (x + w - cw if r else x, 30, cw, 2))
        nm = f.d['n'] if (i == 0 or X['mode'] == 2 or True) else 'CPU'
        T(S, nm, x + w if r else x, 34, al=2 if r else 0)
        for j in range(2):
            S.fill((255, 204, 51) if X['w'][i] > j else (40, 30, 60), (x + w - 6 - j * 9 if r else x + j * 9, 46, 6, 6))
    S.fill((0, 0, 0), (W // 2 - 16, 6, 32, 20)); T(S, str(max(0, X['timer'])), W // 2, 9, (255, 90, 90) if X['timer'] <= 10 else (255, 255, 255), 2, 1)


def portrait(S, d, cx, cy):
    S.fill(d['b'], (cx - 8, cy - 10, 16, 12)); S.fill(d['a'], (cx - 8, cy - 4, 16, 2))
    S.fill(d['s'], (cx - 6, cy - 22, 12, 12)); S.fill(d['h'], (cx - 6, cy - 22, 12, 4)); S.fill((17, 17, 17), (cx + 1, cy - 17, 2, 2))
    lk = d['lk']
    if lk == 0: S.fill(d['a'], (cx - 6, cy - 16, 12, 2))
    elif lk == 1: S.fill(d['h'], (cx - 5, cy - 26, 3, 5)); S.fill(d['h'], (cx, cy - 28, 3, 7)); S.fill(d['h'], (cx + 4, cy - 26, 3, 5))
    elif lk == 2: S.fill(d['a'], (cx - 7, cy - 23, 14, 6))
    elif lk == 3: S.fill(d['h'], (cx - 7, cy - 23, 14, 8)); S.fill(d['h'], (cx - 7, cy - 15, 3, 7))
    else: S.fill(d['a'], (cx - 7, cy - 27, 2, 6)); S.fill(d['a'], (cx + 5, cy - 27, 2, 6))


def render(S):
    s = X['scr']
    if s == 'title':
        S.blit(SF[0], (0, 0)); T(S, 'PIXEL FIGHT', W // 2, 22, (255, 204, 51), 3, 1)
        T(S, '24 lutadores  |  12 mapas  |  estilo M.U.G.E.N', W // 2, 62, al=1)
        for i, t in enumerate(('1 JOGADOR', '2 JOGADORES', 'CPU x CPU', 'SAIR')):
            T(S, ('> ' if i == X['menu'] else '') + t, W // 2, 84 + i * 14, (255, 220, 60) if i == X['menu'] else (255, 255, 255), 2, 1)
        T(S, 'P1: A D W + F G H T    P2: setas + J K L I    defesa: segure para trás', W // 2, 160, al=1)
    elif s == 'sel':
        S.fill((16, 10, 32)); T(S, 'ESCOLHA O LUTADOR: ' + ('JOGADOR 1' if X['who'] == 0 else 'JOGADOR 2'), W // 2, 6, (255, 204, 51), 1, 1)
        for i, d in enumerate(CH):
            cx = 14 + (i % 8) * 38; cy = 18 + (i // 8) * 36
            pg.draw.rect(S, (255, 204, 51) if i == X['sel'] else (60, 50, 90), (cx - 3, cy - 1, 36, 34), 2 if i == X['sel'] else 1)
            portrait(S, d, cx + 15, cy + 28)
        D = CH[X['sel']]; T(S, D['n'], 8, 124, (255, 204, 51), 2)
        T(S, 'Especial: %s   Super: %s' % (KN[D['sp'][0]], KN[D['su'][0]]), 8, 143)
        T(S, 'Vida %d  Velocidade %.1f  %s' % (D['hp'], D['spd'], '  '.join(PN[k] for k in D['pas']) or 'Sem passiva'), 8, 156)
    elif s == 'map':
        S.blit(SF[X['mi']], (0, 0)); T(S, '< ' + MAPS[X['mi']]['n'] + ' >', W // 2, 8, (255, 255, 255), 2, 1)
        T(S, '%d/%d   Enter para lutar' % (X['mi'] + 1, len(MAPS)), W // 2, 160, al=1)
    else:
        S.blit(SF[X['mi']], (0, 0)); ox = oy = 0
        if X['shake']: ox = random.randint(-2, 2); oy = random.randint(-2, 2)
        B = S.copy() if X['shake'] else None
        for m in MN: S.fill(m['c'] if X['t'] % 20 < 10 else (255, 255, 255), (int(m['x']) - 3, GY - 3, 6, 3))
        for f in P: draw_f(S, f)
        for p in PJ:
            r = (int(p['x'] - p['w'] / 2), int(p['y'] - p['h'] / 2), int(p['w']), int(p['h']))
            S.fill(p['c'], r)
            if p.get('beam'): S.fill((255, 255, 255), (r[0], r[1] + r[3] // 3, r[2], max(2, r[3] // 3)))
            elif p['w'] > 8: S.fill((255, 255, 255), (r[0] + 3, r[1] + 3, r[2] - 6, r[3] - 6))
            else: S.fill((255, 255, 255), (r[0] + 2, r[1] + 2, max(1, r[2] - 4), max(1, r[3] - 4)))
        for q in PT: S.fill(q[5], (int(q[0]), int(q[1]), 2, 2))
        if X['shake']: S.blit(S.copy(), (ox, oy)); S.fill((0, 0, 0), (0, 0, 0, 0))
        hud(S); st = X['st']
        if st == 'intro':
            T(S, 'RODADA %d' % X['rd'], W // 2, 78, (255, 204, 51), 2, 1) if X['t'] < 60 else T(S, 'LUTE!', W // 2, 76, (255, 90, 70), 3, 1)
        if st == 'rend': T(S, X['msg'], W // 2, 76, (255, 204, 51), 3, 1)
        if s == 'over':
            S.fill((0, 0, 0), (40, 60, 240, 56)); T(S, X['res'], W // 2, 70, (255, 204, 51), 2, 1); T(S, 'Enter para voltar ao menu', W // 2, 98, al=1)


# ---------------- ENTRADA / MAIN ----------------
K1 = {pg.K_a: 'l', pg.K_d: 'r', pg.K_w: 'u', pg.K_f: 'punch', pg.K_g: 'kick', pg.K_h: 'sp', pg.K_t: 'su'}
K2 = {pg.K_LEFT: 'l', pg.K_RIGHT: 'r', pg.K_UP: 'u', pg.K_j: 'punch', pg.K_k: 'kick', pg.K_l: 'sp', pg.K_i: 'su'}
NAV = {pg.K_a: 'l', pg.K_LEFT: 'l', pg.K_d: 'r', pg.K_RIGHT: 'r', pg.K_w: 'u', pg.K_UP: 'u', pg.K_s: 'd', pg.K_DOWN: 'd',
       pg.K_RETURN: 'ok', pg.K_SPACE: 'ok', pg.K_f: 'ok', pg.K_j: 'ok', pg.K_ESCAPE: 'bk', pg.K_BACKSPACE: 'bk'}


def menu_key(key):
    a = NAV.get(key); s = X['scr']
    if not a: return
    if s == 'title':
        if a in ('u', 'd'): X['menu'] = (X['menu'] + (1 if a == 'd' else -1)) % 4
        elif a == 'ok':
            if X['menu'] == 3: pg.quit(); sys.exit()
            X['mode'] = (1, 2, 0)[X['menu']]; X['who'] = 0; X['sel'] = 0; n = len(CH)
            if X['mode'] == 0: X['c'] = [random.randrange(n), random.randrange(n)]; X['scr'] = 'map'
            else: X['scr'] = 'sel'
    elif s == 'sel':
        n = len(CH); i = X['sel'] + {'l': -1, 'r': 1, 'u': -8, 'd': 8}.get(a, 0); X['sel'] = i % n
        if a == 'ok':
            X['c'][X['who']] = X['sel']
            if X['who'] == 0 and X['mode'] == 1: X['c'][1] = random.randrange(n); X['scr'] = 'map'
            elif X['who'] == 0: X['who'] = 1
            else: X['scr'] = 'map'
        elif a == 'bk':
            if X['who'] == 1: X['who'] = 0
            else: X['scr'] = 'title'
    elif s == 'map':
        n = len(MAPS)
        if a in ('l', 'u'): X['mi'] = (X['mi'] - 1) % n
        elif a in ('r', 'd'): X['mi'] = (X['mi'] + 1) % n
        elif a == 'ok': X['w'] = [0, 0]; X['rd'] = 1; new_round()
        elif a == 'bk': X['scr'] = 'sel'; X['who'] = 0
    elif s == 'over' and a == 'ok': X['scr'] = 'title'


def main():
    pg.init()
    try:
        pg.mixer.init(22050, -16, 1)
        SN.update(hit=mk_snd(110, .08), blk=mk_snd(200, .05), ko=mk_snd(60, .4), whoosh=mk_snd(320, .04, .06), spec=mk_snd(500, .12, .08))
    except Exception: pass
    win = pg.display.set_mode((960, 540), pg.RESIZABLE); pg.display.set_caption('PIXEL FIGHT')
    S = pg.Surface((W, H)); clk = pg.time.Clock()
    SF[:] = [make_map(m) for m in MAPS]
    X.update(scr='title', sel=0, c=[0, 1], w=[0, 0], rd=1, mi=0, who=0, mode=1, menu=0, st='intro', t=0, timer=60, tick=0,
             shake=0, stop=0, msg='', res='', ai=dict(t=0, a='fwd'), ai0=dict(t=0, a='fwd'))
    P[:] = [F(CH[0], 100, 1, 0), F(CH[1], 220, -1, 1)]
    while True:
        for ev in pg.event.get():
            if ev.type == pg.QUIT: return
            if ev.type in (pg.KEYDOWN, pg.KEYUP):
                dn = ev.type == pg.KEYDOWN
                if dn and ev.key == pg.K_F11: pg.display.toggle_fullscreen()
                if X['scr'] == 'fight':
                    if dn and ev.key == pg.K_ESCAPE: X['scr'] = 'title'; continue
                    if X['mode']:
                        if ev.key in K1: press(0, K1[ev.key], dn)
                        if ev.key in K2: press(1 if X['mode'] == 2 else 0, K2[ev.key], dn)
                elif dn: menu_key(ev.key)
        if X['scr'] == 'fight': upd()
        render(S)
        ww, wh = win.get_size(); sc = min(ww / W, wh / H); sz = (int(W * sc), int(H * sc))
        win.fill((0, 0, 0)); win.blit(pg.transform.scale(S, sz), ((ww - sz[0]) // 2, (wh - sz[1]) // 2))
        pg.display.flip(); clk.tick(60)


if __name__ == '__main__':
    main()
