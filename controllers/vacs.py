# coding: utf8
import datetime

time_expire = 300
# выберим тип имущества - фиат, крипта или имущество
@cache.action(time_expire=time_expire, cache_model=cache.ram, vars=True, public=True, lang=True)
def index():
    session.forget(response)
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire)
    return locals()

def fonds():
    res = CAT(H3(T('Как начисляются поощрения')),
              T('Если пайщик ввел при регистрации Ваш "код партнера" как свой "подарочный код", то он стал вашим приглашенным (рефералом).'), BR(),
              T('Если у данного фонда есть начисления за поощрения, то с каждого взноса в этот фонд от вашего реферала Вы получаете поощрения. Причем если в этот фонд делает взнос реферал вашего реферала, то Вы тоже получаете поощрение, но в несколько раз меньше - согласно делению на "делитель на уровень поощрения". И так далее до "максимальной глубины уровней". '), BR(),
              T('Например, Вы пригласили 4-х пайщиков, с каждого из которых Вы получили 300 рублей поощрения, что равно 1200р. Если каждый из ваших рефералов тоже пригласит 4-х, то вы получите еще 300/3*4*4 = 1600р. Следующий уровень Вам принесет уже 300/3/3*4*4*4 = 2133. Четвертый уровень даст 2844, а 5-й - 3792. В сумме 11570 рублей.'), BR(),
              T('Если Вы ассоциативный пайщик, то величина начислений уменьшается в 2 раза.'), BR()
              )
    
    res += CAT(H3(T('Список процентов и сумм поощрений за взносы от пайщиков, которых Вы пригласили по своему "подарочному коду"')))
    for rr in db(db.fonds.id == db.fond_calcs.fond_id).select(orderby=~db.fonds.wei):
        r = rr.fond_calcs
        f = rr.fonds
        p = db.progs[f.prog_id]
        if r.perc:
            vol = '%s' % r.perc + '%'
        else:
            vol = r.vol
        res += CAT(vol, ' ', T('в программе'),' ',A(B(p.name), _href=URL('progs','index',args=[p.id])),
                   ' ', T('за взносы в '),' ',B(f.name),
                   '. ', T('Деление на уровень поощрения:'),' ', B(r.lvl_div),
                   ', ', T('максимальная глубина поощрений:'),' ', B(r.lvl_max),BR(),BR())
    return dict(res=res)
