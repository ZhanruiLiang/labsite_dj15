from __future__ import print_function

# open('/tmp/debug.log', 'w').close()
def dprint(*args, **kwargs):
    # f = open('/tmp/debug.log', 'a')
    print(*args, file=f, **kwargs)
    # f.close()
