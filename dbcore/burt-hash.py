# see http://burtleburtle.net/bob/hash/integer.html
hash_constants = '''
38 113  41  68  35  74 111
38 113  42  69  35  73 112
38 114   9 100  35 107  46
38 114  11  66   8  68 112
38 114  42  69  35  73 112
38 114  78  37  71  35 111
39 113  41  68   2  74 112
39 114   9 101   2 107  17
39 114   9 101   2 107  49
39 114  37  99  39 109  50
39 115  36  67  38  44 112
39 115  37  70  35 110  11
39 115  41  74  36  67 111
39 116   4 104   6 107  16
39 116  10 101   8  75 113
40 113  12  99  39  69 112
40 113  13  99   6  69 113
40 113  38 101   2 106  16
40 113  38 101   2 106  48
40 114   3 102   8 109  15
40 114  37  99   7  77 113
41 113  11 100   7  69 111
42 114  44  99  38  72 113
43 115   7 101   3 109  48
44 114  36 105  38 108  16
44 114  37 102  35 107  16
44 114  41 101   2 109  16
45 113  37 102   3 108  47
45 113  37 105  35 104  17
45 113  37 105  35 104  47
45 113  39  99  37  76 111
45 113  42 101   2 109  46
45 113  42 101   2 109  50
46 113  42 101  35 110  47
46 113  42 101  35 110  50
'''

def op2code(c):
    c = int(c)
    if c < 32:
        return 'x += x << %d' % c
    elif c < 64:
        return 'x -= x << %d' % (c-32)
    elif c < 96:
        return 'x ^= x << %d' % (c-64)
    else:
        return 'x ^= x >> %d' % (c-96)
    
def emit_python(name, clist):
    print 'def %s(x):' % name
    for c in clist:
        print '\t%s' % op2code(c)
    print '\treturn x\n'

def emit_c(name, clist, xtype='uint32_t'):
    print 'static {xtype} {name}({xtype} x) {{'.format(name=name, xtype=xtype)
    for c in clist:
        print '\t%s;' % op2code(c)
    print '\treturn x;\n}\n'

def emit_c_obj(name, clist, xtype='uint32_t'):
    print 'struct %s : burt_hash {' % name
    print '\t{xtype} operator()({xtype} x) {{'.format(name=name, xtype=xtype)
    for c in clist:
        print '\t\t%s;' % op2code(c)
    print '\t\treturn x;\n\t}\n};\n'

def emit_c_epilogue(nlists, name):
    print '{name}::function * {name}::select_hash(uint32_t selector) {{'.format(name=name);
    print '\tswitch(selector %% %d) {' % nlists
    print '\tdefault:'
    for i in range(nlists):
        print '\tcase {i}: return &hash{i};'.format(i=i)
    print '\t}\n}\n'

def emit_c_prologue(nlists):
    print '''
/***************************************************
 * * *                                         * * *
 * * *      * * * DO NOT MODIFY * * *          * * *
 * * *                                         * * *
 * * * Automatically generated by burt-hash.py * * *
****************************************************/
#include "burt-hash.h"
    
'''

i=0
lists = [clist.split() for clist in hash_constants.splitlines() if clist]

#dbg = ['{%s}' % c for clist in lists for c in clist]
#print ' '.join(dbg)

# in hardware, limit the number of expensive add/sub we use
addsub_limit = 5
lists = [clist for clist in lists
         if sum(1 for c in clist if int(c) < 64) < addsub_limit]

# emit the code
emit_c_prologue(len(lists))
for i,clist in enumerate(lists):
    classes = []
    for c in clist:
        c = int(c)
        if c < 32:
            classes.append(0)
        elif c < 64:
            classes.append(1)
        elif c < 96:
            classes.append(2)
        else:
            classes.append(3)

    emit_c('hash%d' % i, clist, 'uint32_t')
    emit_c('hash%d' % i, clist, '__v4si')

# now the epilogue
emit_c_epilogue(len(lists),'burt_hash')
emit_c_epilogue(len(lists),'burt_hash4')
    


            