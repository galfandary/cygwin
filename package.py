#!/usr/bin/env python3

class PackageData:
    def __init__(self,pkg):
        self.pkg = pkg
        self.file = None
        self.deps = set()

def ST(fp):
    ST.pkg = {}
    ST.alt = {}
    pkg = None
    data = None
    def csplit(x):
        return [i.strip() for i in x.split(',')]
    for line in fp:
        if line[0] == '#':
            continue
        if line[0] == '@':
            pkg = line[1:].strip()
            data = PackageData(pkg)
            continue
        if line[0] == '[':
            data = PackageData(pkg)
            continue
        if pkg is None: continue
        if data is None: continue
        try: n,v = line.split(': ')
        except: continue
        v = v.strip()
        if not v: continue
        if n == 'version':
            if pkg not in ST.pkg:
                ST.pkg[pkg] = data
            ST.pkg['%s-%s'%(pkg,v)] = data
            data.ver = v
        elif n == 'install':
            try: f,s,h = v.split()
            except: continue
            data.file = f
            data.size = s
            data.hash = h
        elif n == 'requires':
            data.deps |= set(v.split())
        elif n == 'depends2':
            data.deps |= set(csplit(v))
        elif n == 'provides':
            for p in csplit(v):
                a = ST.alt.get(p,[])
                if not a: ST.alt[p] = a
                a.append(data)
    return 0

# Known Bugs:
DEP_BUG = {
    'tzcode' : set(),
    'terminfo' : set(),
    'terminfo-extra' : set(),
}

def dependencies(names,hashs,order,d):
    bug = DEP_BUG.get(d.pkg)
    if bug is not None: d.deps = bug
    level = 0
    for p in d.deps:
        c = addToList(names,hashs,order,p)
        if not c: return None
        try: l = c.level + 1
        except:
            l = 0
            print('Cyclic dependency:',d.pkg)
        if l > level: level = l
    d.level = level
    return 0

def addToList(names,hashs,order,pkg):
    d = names.get(pkg)
    if d: return d
    d = ST.pkg.get(pkg)
    names[pkg] = d
    if not d or not d.hash:
        print('No match for:',pkg)
        return None
    h = hashs.get(d.hash)
    if h: return h
    hashs[d.hash] = d
    dependencies(names,hashs,order,d)
    order.append(d)
    return d

def update_db(fin,fout,pkgs):
    db = {}
    with open(fin) as fp:
        for line in fp:
            try: pkg,ver = line.strip().split(',')
            except: continue
            db[pkg] = ver
    pks = []
    for d in pkgs:
        p,v = d.pkg,d.ver
        if v == db.get(p): continue
        db[p] = v
        pks.append(d)
    with open(fout,'w') as fp:
        for i in sorted(db.items()):
            print(','.join(i),file=fp)
    return pks

def do_install(args):
    names,hashs,order = {},{},[]
    for p in args.pkg:
        if not addToList(names,hashs,order,p):
            return -1
    lines = []
    if args.upd:
        order = update_db(args.idb,args.odb,order)
    for d in order:
        l = str(1000000 + d.level)
        a = (l,d.pkg,d.ver,d.file,d.hash)
        lines.append(','.join(a))
    for line in sorted(lines):
        print(line)
    return 0

def provides(pkgs):
    for p,a in pkgs.items():
        m = {}
        v = {}
        for d in a:
            if not d.file: continue
            m[d.pkg] = d
            v[d.ver] = d
        n = len(m)
        if n != 1:
            e = 'More then one' if n > 1 else 'No'
            print('%s provider for: %s'%(e,p))
            return -1
        v = sorted(v.items())
        d = v[-1][1]
        ST.pkg[p] = d
    return 0

def run(args):
    with open(args.ini) as fp: ST(fp)
    if provides(ST.alt) < 0: return -1
    return do_install(args)

if __name__ == '__main__':
    from argparse import ArgumentParser as Parser
    parser = Parser(description='Cygwin Package Manager')
    a = parser.add_argument
    a('cmd',type=str,help='Command')
    a('pkg',type=str,help='Packages',nargs='*')
    a('-i','--ini',type=str,help='Setup File',
      default='/etc/setup/setup.ini')
    a('-d','--idb',type=str,help='Installed Packages',
      default='/etc/setup/installed.csv')
    a('-o','--odb',type=str,help='Updated Packages',
      default='/tmp/installed.csv')
    a('-u','--upd',help='Update',default=False,action='store_true')
    exit(run(parser.parse_args()))