# coding: utf8
# try something like

import common
if common.not_is_local(): raise HTTP(200, T('local ERROR'))


# пересчитать заново всех входы во счету-фонда
# http://127.0.0.1:8000/polza/tools/recalc_x_order/main
def recalc_x_order_one():
    import fonds
    cod = request.args[0]
    fonds.recalc_x_order(db, cod)
    # и запустить уведомление от криптоПай по этому счету
    redirect(URL('cp','resp', vars={'order':cod}))

# проверка вручную чего там есть на криптопай
# http://127.0.0.1:8000/polza/tools/cp_resp?order=main
def cp_resp():
    redirect(URL('cp','resp',vars=request.vars))

# пересчитать заново все входы по всем фондам
# http://127.0.0.1:8000/polza/tools/recalc_x_order/main
def recalc_x_orders():
    import fonds, cpay_lib
    fs = db(db.fonds).select()
    for f in fs:
        fonds.recalc_x_order(db, f.cod)
    # теперь удалим ордера все и заново их
    db.orders.truncate()
    db.good_rates.truncate()
    mess = ''
    for f in fs:
        id = db.orders.insert ( name = f.cod, fond_id = fond.id )
        order = db.orders[id]
        mess = mess + '<br>order created<br>'
        mess = mess + '<br> info: %s<br>=====<br>' % cpay_lib.get_info_last(db, order)
    return mess

def clear_ALL_trans_and_bals():
    return 'точно нужно удалить все транзакции? лучше пересчитать - resum_ALL<br>заглушку выключить'
    import fonds
    fonds.clear_ALL(db)

# на основе текущих транзакций пересчет всех сумм
# тоесть транзакции не трогает
def resum_tr():
    import fonds
    if request.args(0):
        fonds.resum(db, request.args(0)) # , trans=None, negotiate=None)
        #db.rollback()
        return 'resum_ALL now'
    return 'type resum_tr/22'
# на основе текущих транзакций пересчет всех сумм
# тоесть транзакции не трогает
def resum_ALL():
    import fonds
    return fonds.resum_ALL(db)
    

def rand():
    import addrgen, base58, os
    prt_rec = True
    while prt_rec:
        prt_cod = base58.b58encode(os.urandom(6))
        #prt_cod = addrgen.base58_encode(os.urandom(6))
        print prt_cod
        prt_rec = db(db.members.prt_cod == prt_cod).select().first()
    return prt_cod

# выберим тип имущества - фиат, крипта или имущество
@cache.action(time_expire=36, cache_model=cache.ram, vars=False, public=True, lang=True)
def index():
    return dict()

# http://127.0.0.1:8000/polza/tools/rate_on_dt/3/6?dt=14-06-26%2012:23:22
def rate_on_dt():
    if len(request.args)<2:
        return 'need /item_id1/item_id2?dt=14-06-26%2012:23:22'
    c1 = int(request.args[0])
    c2 = int(request.args[1])
    import rates, datetime
    dt = request.vars['dt']
    dt = datetime.datetime.strptime(dt, '%y-%m-%d %H:%M:%S')
    #tab = 'unit'
    rate = rates.get_income_on_dt(db,'unit_rates', c1,c2, dt)
    return '1 %s -> %s = %s' % (db.units[c1].name, db.units[c2].name, rate)

#
#(db7p.deal_accs.acc.contains('@')) & (db7p.deal_accs.acc.contains('.'))
def spam():
    return 'stopped'
    mess = '''
    Здравствуйте!
    
    И так нас зарегистрировали. Название выбрано нейтральное что бы не привлекать внимание на начальных этапах и при регистрации:
    Инновационное Постребительское Общество "Польза"
    
    Открыт расчетный счет в СберБанке, теперь можно вносить взносы.
    
    Запущен сайт ipo-polza.ru
    На нем можно регистрироваться и оплачивать вступительные взносы
    
    Созданы программы:
    1. "получи 500 рублей приведя своих друзей"
    2. вклад 37,77% за 777 дней (или 18% годовых)
    
    Для получения новостей, подключайтесь в социальной сети google+ к пользователю ipo.polza@gmail.com

    
    С Уважением, Дмитрий Ермолаев
    http://ipo-polza.ru
'''
    addrs = {}
    tab = db7p((db7p.deal_accs.acc.contains('@')) & (db7p.deal_accs.acc.contains('.'))).select()
    for r in tab:
        addrs[r.acc]=1
    for r in db7p(db7p.news_descrs).select():
        addrs[r.email]=1

    i = 0
    to = []
    for k in addrs:
        print k
        i = i + 1
        to.append(k)
        if i > 5:
            common.send_email_to_descr(to,'Стартап стартует!', mess,
                   #locals(),'invite/accept_email.html', response,
                   None, None, None, settings
                   )
            i = 0
            to = []

def items_conv():
    return 'NOT use!'
    tab = 'item0s'
    db[tab].truncate()
    for r in db(db.items1).select():
        v = { 'unit_id': r.unit1 }
        for f in db[tab]._fields:
            if f == 'unit_id': continue
            v[f] = r[f]
        id = db[tab].insert(**v)

def url_probe():
    f = db.fonds[request.args(0)]
    if not f: return 'fond not found'
    ### !!!! обязательно COPY !!!! чтобы не влиять на других
    vars = settings.CP_URL_VARS.copy()
    vars['order'] = f.cod
    if f.cp_pars:
        #print f.cp_pars
        vars.update(f.cp_pars)
    url = URL(*settings.CP_URL_PATH, vars=vars, **settings.CP_URL_PARS)
    return f.name + ' %s ' % url

def conv_to_2():
    db.goods.truncate()
    return 'truncated'
    import db_conv
    return db_conv.to_2(db_old, db)
