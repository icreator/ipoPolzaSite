# coding: utf8
# try something like
def index():
    id = request.args(0)
    if id:
        try:
            r = db.news[id]
        except:
            return 'err'
        tt = CAT(H4(r.ev and (T('Событие состоится: '), r.ev) or r.on_create),
                 H4(r.ur and A(r.hd, _href=r.ur, _target="_blank") or r.hd),
                 r.tx,
                 BR(),BR(),
                 A(T('Все новости и события'), _href=URL('index'))
                 )
    else:
        tt = []
        for r in db(db.news).select(orderby=~db.news.on_create):
            tt.append( H5(r.on_create,' ',A(r.hd, _href=URL(args=[r.id])))
                )
    
    return locals()
