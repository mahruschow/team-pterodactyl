"""Minimal S-expression reader/writer for KiCad files (no dependencies)."""
import re

_TOKEN=re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))',re.S)
_ESCAPE=re.compile(r'\\(.)')


class Sym(str):
    """Unquoted atom."""


def parse(text):
    stack=[[]];pos=0
    while True:
        m=_TOKEN.match(text,pos)
        if not m or m.end()==pos:break
        pos=m.end();o,c,s,a=m.groups()
        if o:stack.append([])
        elif c:
            node=stack.pop();stack[-1].append(node)
        elif s is not None:stack[-1].append(_ESCAPE.sub(lambda e:{'n':'\n'}.get(e.group(1),e.group(1)),s[1:-1]))
        else:stack[-1].append(Sym(a))
    assert len(stack)==1
    return stack[0][0]


def quote(s):
    return '"'+str(s).replace(chr(92),chr(92)*2).replace('"',chr(92)+'"').replace('\n',chr(92)+'n')+'"'


def dump(node,indent=0):
    if isinstance(node,list):
        if all(not isinstance(x,list) for x in node):return '('+' '.join(dump(x) for x in node)+')'
        out='('+' '.join(dump(x) for x in node if not isinstance(x,list))
        for x in node:
            if isinstance(x,list):out+='\n'+'\t'*(indent+1)+dump(x,indent+1)
        return out+'\n'+'\t'*indent+')'
    if isinstance(node,Sym):return str(node)
    if isinstance(node,bool):return 'yes' if node else 'no'
    if isinstance(node,float):return ('%.4f'%node).rstrip('0').rstrip('.')
    if isinstance(node,int):return str(node)
    return quote(node)


def find(node,key):
    return [x for x in node if isinstance(x,list) and x and x[0]==key]


def first(node,key):
    r=find(node,key);return r[0] if r else None
