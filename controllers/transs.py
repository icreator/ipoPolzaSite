# coding: utf8

# кто-то грузит наш сервер -
##91.207.60.88 - - [03/Mar/2015:08:24:06 +0300] "GET /polza/transs/index/fonds/orders.fond_id/4/?keywords=../.../.././../.../.././../.../.././../.../.././../.../.././../.../.././windows/win.ini&order=orders.id&_export_type=json 
# порадуем его 40к х
class Jammer():
   def read(self,n): return 'x'*n
def jam(): return response.stream(Jammer(),40000)

if '_export_type' in request.vars:
    #redirect('http://google.com')
    ##redirect(URL('jam'))
    raise HTTP(201, jam())
    #raise HTTP(200,'stop...')

    
import common, datetime

#print request.function
if common.not_is_local() and request.function not in ['index', 'download']:
    raise HTTP(200, T('local ERROR'))

def download(): return response.download(request,db)

time_expire = request.is_local and 3 or 300

# выберим тип имущества - фиат, крипта или имущество
@cache.action(time_expire=time_expire, cache_model=cache.ram, vars=True, public=True, lang=True)
def index_old():
    session.forget(response)
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire)

    t = request.args(0)
    if t:
        try:
            t = SQLFORM.smartgrid(db[t],
              maxtextlengths = { 'fonds.name': 60, 'fonds.info': 200 },
              upload=URL('download'),
              links_in_grid=False,
              csv=False,
              )
        except:
            t = 'err'
    return locals()

def index():
    session.forget(response)
    dt_expire = datetime.timedelta(0, time_expire)

    h = CAT(
        P(T('Все записи о взносах будут внесены блокчейн-среду нашего проекта'), ' ',
          A('DATACHAINS.WORLD', _href='http://datachains.world', _target='blank'))
    )
    return dict(h = h)

def fiat_add():
    bacc_id = request.args(0)
    if not bacc_id.isdigit():
        return jam()

    bacc = bacc_id and db.memb_b_accs[bacc_id]
    if not bacc:
        redirect(URL('fiat'))
    memb = db.members[bacc.member_id]
    form = SQLFORM(db.trans, fields=['fond_id', 'good_id', 'amo', 'txid', 'on_create', 'info'])
    form.vars.b_acc_id = bacc_id
    form.vars.memb_id = memb.id
    res = None
    if form.process().accepted:
        # транзакция уже задана
        trans = db.trans[form.vars.id]
        # тут надо все суммы пересчитать
        # найдем фонд который задали
        fond = db.fonds[trans.fond_id]
        # возьмем трнзакцию что создали
        # закатаем туда учетный фонд
        trans.update_record(
            from_fond_id = db.fonds[fond.unret and settings.FOND_CALC_UNRET or settings.FOND_CALC_RET].id,
            #amo_out = trans.amo,
            )
        import fonds
        res = fonds.resum(db, None, trans)
        if res:
            redirect(URL('fiat', vars={'mess': T('Транзакция добавлена')}))
    return locals()
# если пришли фиатные деньги - то по номеру счета и ИД банка или системы денег
# определяем пайщика
def fiat():
    if request.vars.get('mess'):
         response.flash = request.vars.get('mess')

    form = FORM(T('Укажите реквизиты платежа:'),
             LABEL(T('БИК (пусто если наличными)')), INPUT(_name='bik'),
             LABEL(T('СЧЕТ')), INPUT(_name='acc'),
             BR(), INPUT(_value=T('Продолжить'), _type='submit'))
    if form.process().accepted:
        if not form.vars.bik:
            # если пусто - значит за наличные
            redirect(URL('fiat_add'))
        bacc = db((db.memb_b_accs.bik==form.vars.bik)
              & (db.memb_b_accs.acc==form.vars.acc)).select().first()
        if not bacc:
            response.flash = T('Таких реквизитов не найдено')
        else:
            redirect(URL('fiat_add', args=[bacc.id]))
    return locals()

#############################
def crypto_add():
    xacc_id = request.args(0)
    if not xacc_id.isdigit():
        return jam()

    xacc = xacc_id and db.memb_x_accs[xacc_id]
    if not xacc:
        redirect(URL('crypto'))
    memb = db.members[xacc.member_id]
    form = SQLFORM(db.trans, fields=['fond_id', 'good_id', 'amo', 'txid', 'info'])
    form.vars.x_acc_id = xacc_id
    form.vars.memb_id = memb.id
    res = None
    if form.process().accepted:
        # тут надо все суммы пересчитать
        import fonds
        res = fonds.resum(db, form.vars.id)
        if res:
            redirect(URL('crypto', vars={'mess': T('Транзакция добавлена')}))
    return locals()

def crypto():
    if request.vars.get('mess'):
         response.flash = request.vars.get('mess')

    form = FORM(T('Укажите адрес плательщика:'),
             LABEL(T('Адрес')), INPUT(_name='addr'),
             BR(), INPUT(_value=T('Продолжить'), _type='submit'))
    if form.process().accepted:
        xacc = db((db.memb_x_accs.addr==form.vars.addr)).select().first()
        if not xacc:
            response.flash = T('Такого адреса у пайщиков не найдено')
        else:
            redirect(URL('crypto_add', args=[xacc.id]))

    return locals()

def item():
    if request.vars.get('mess'):
         response.flash = request.vars.get('mess')

    form = SQLFORM(db.trans)
    res = None
    if form.process().accepted:
        # тут надо все суммы пересчитать
        import fonds
        res = fonds.resum(db, form.vars.id)
        if res:
            mess = T('Транзакция добавлена: <br>%s') % res
            response.flash = mess

    return BEAUTIFY(locals())

# http://127.0.0.1:8000/polza/transs/resum/trans_calc/1
# http://127.0.0.1:8000/polza/transs/resum/trans/1
def resum():
    t = request.args(0)
    if t and not t.isdigit():
        return jam()
    t1 = request.args(1)
    if t1 and not t1.isdigit():
        return jam()

    import fonds
    try:
        trans = db[t][t1]
        fonds.resum(db, trans)
    except:
        return 'err'
