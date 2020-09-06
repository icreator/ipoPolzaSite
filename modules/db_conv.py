#!/usr/bin/env python
# coding: utf8
#from gluon import *

def copy_tab(db_old, db, t_old, t):
    db[t].truncate()
    fields = db[t].fields
    fields_old = db_old[t_old].fields
    for r in db_old(db_old[t_old]).select():
        print r
        p = {}
        for f in fields:
            if f in fields_old:
                p[f] = r[f]
        db[t].insert (**p)
        pass

def copy_as_is(db_old, db, tabs):
    for t in tabs:
        copy_tab(db_old, db, t, t)
        pass

def to_2(db_old, db):
    db.goods.truncate()
    return 'stop'
    repl_tabs = {'item0s':'items' }
    copy_as_is(db_old, db, ['b_accs', 'faces', 'f_invite',
            'members', 'meet_names', 'memb_cons','memb_meets','memb_audits', # 'memb_b_accs',
            'memb_x_accs','members_add5','members_add_x','units', 'props'])
    # переименуем
    copy_tab(db_old, db, 'items_cat0', 'goods_cat0')
    copy_tab(db_old, db, 'items_cat1', 'goods_cat1')
    copy_tab(db_old, db, 'item0s', 'goods')
    copy_as_is(db_old, db, ['projects','progs','fonds','fond_calcs','trans'])
    copy_as_is(db_old, db, ['orders', 'order_txids', 'news'])
    return 'OK'
