# Client for drv_server.py:  python3 drv.py <cmd> [key=value ...]
#   goto url=... [wait=ms]   text [sel=] [frame=] [grep=] [max=] [off=]   links [grep=]
#   buttons [grep=] [sel=]   click sel=|text=|role=+name= [nth=] [wait=]   fill sel= value=
#   type sel= value= [clear=1]   press key=   select sel= value=|label=   options sel=
#   shot path= [sel=] [full=1]   eval js=   frames   pages   switch idx=   back   net [grep=] [xhr=1]
#   body i=   html sel= [max=]   scroll dy=   xy x= y=   wait wait=ms   dialogs   quit
import json, os, socket, sys
SOCK = os.environ.get('DRV_SOCK') or os.path.expanduser('~/.cache/ekko-drv.sock')
req = {'cmd': sys.argv[1]}
for a in sys.argv[2:]:
    k, _, v = a.partition('=')
    req[k] = v
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.settimeout(240)
s.connect(SOCK)
s.sendall((json.dumps(req) + '\n').encode())
buf = b''
while not buf.endswith(b'\n'):
    c = s.recv(1 << 20)
    if not c:
        break
    buf += c
r = json.loads(buf.decode())
print(('' if r['ok'] else 'ERROR: ') + str(r['out']))
