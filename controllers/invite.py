# coding: utf8
from decimal import Decimal

import common

ADD_FIELDS = ['email', 'addr', 'face_id', 'b_date']
def get_members_add5():
    rec = db(db.members.email==request.vars.get('email')).select().first()
    #print 'get_members_add5 1', rec
    if rec:
        rec = "jQuery('#hidden').fadeOut('1755'); jQuery('#submit').fadeOut('755'); jQuery('#targ').html('%s')" % T('Такой пайщик уже принят!')
        return rec

    rec = db(db.members_add5.email==request.vars.get('email')).select().first()
    #print 'get_members_add5 2', rec
    if rec:
        # тут в адресе есть спец. символы - наклонные черты и пр - их надо отдельно присоединять
        ttt = TABLE(*[TR(k, '%s' % v) for k,v in rec.iteritems() if k in ['email', 'face_id', 'b_date']])
        #print rec.addr
        ttt = '%s <BR> %s <br>' % (ttt, '')
        #import urllib
        #ttt = ttt + urllib.unquote(urllib.urlencode({'addr':rec.addr}))

        #ttt = ttt.decode('ascii')
        #ttt = urllib.quote( ttt )
        #print 'TABLE:\n', ttt
        #return
        #ttt = CAT(rec,LABEL(T('Заполните данные:')),LABEL(T('Имя')), INPUT(_name='f_name'),
        #          LABEL(T('Отчество')), INPUT(_name='m_name'),
        #          LABEL(T('Фамилия')), INPUT(_name='l_name'))
        if rec.face_id ==1:
            fff = "jQuery('#fio_name').show(); jQuery('#y_name').hide(); "
        else:
            fff = "jQuery('#y_name').show(); jQuery('#fio_name').hide(); "
        #rec = fff + "jQuery('.hidden').fadeIn('755'); jQuery('#submit').fadeIn('755'); jQuery('#targ1').html('%s')" % ttt
        rec = fff + "jQuery('.hidden').fadeIn('755'); jQuery('#targ1').html('%s')" % ttt
    else:
        rec = "jQuery('.hidden').fadeOut('755'); jQuery('#targ1').html('%s')" % T('Не найдено')
    #print 'EVAL:\n',rec
    return rec

def accept_rec(rec, vars={ 'minor': True }):
    import os, random, addrgen

    upd = {}

    # найдем пригласившего
    inv_cod = rec.inv_cod
    inv_rec = inv_cod and db(db.members.prt_cod == inv_cod).select().first()
    if inv_rec:
        upd['inv_id'] = inv_rec.id

    # перепишем поля что разрешены в ADD_FIELDS
    for (k,v) in rec.iteritems():
        if k in ADD_FIELDS:
            upd[k]=v
    for (k,v) in vars.iteritems():
        if k not in ['check']:
            upd[k]=v

    # сгенерируем ему код партнера
    prt_rec = True
    while prt_rec:
        #print addrgen.base58_encode(99999999)
        prt_cod = addrgen.base58_encode(random.randint(9999999, 99999999999))[:8]
        #prt_cod = base58.b58encode(os.urandom(6))[:8]
        #print prt_cod
        prt_rec = db(db.members.prt_cod == prt_cod).select().first()
    upd['prt_cod'] = prt_cod

    if not upd.get('amo'): upd['minor']=True

    memb_id = db.members.insert( **upd)

    for addr in db(db.members_add_x.ref_id == rec.id).select():
        db.memb_x_accs.insert(member_id = memb_id, addr = addr.addr )
    # и удалим из списка вступающих
    del db.members_add5[ rec.id ]
    return memb_id

# отошлем письмо
def accept_rec_mail(rec, locs):
    common.send_email_to_descr([rec.email, 'icreator@mail.ru'],'ИПО "Польза" прием в пайщики - принятие', None,
           locs,'invite/accept_email.html', response, settings)
    return response.render('invite/accept_email.html',locs)

def accept():
    import common
    if common.not_is_local(): raise HTTP(200, T('ERROR'))
    l = SQLFORM.smartgrid(db.members_add5)
    f=FORM(T('Принять пайщика'), LABEL(T('Введите емайл')),
        INPUT(_name='email'),
        INPUT(_value=T('Принять как ассоциативного'), _type='submit', _id='submit', _class=''),
        INPUT(_value=T('Проверить'), _name='check', _type='button',
            # jQuery(this).parent().html('%s')" % IMG(_src=URL('static','images/loading.gif'), _width=64)
            _onclick="jQuery('#targ').html('%s'); ajax('%s', ['email'], target=':eval')"
                % (IMG(_src=URL('static','images/loading.gif'), _width=28), URL('get_members_add5'))),
        BR(),DIV(_id='targ1'),
        DIV(CAT(
                  DIV(LABEL(T('ИНН')), INPUT(_name='inn'),
                  LABEL(T('Имя')), INPUT(_name='f_name'),
                  LABEL(T('Отчество')), INPUT(_name='m_name'),
                  LABEL(T('Фамилия')), INPUT(_name='l_name') , _id='fio_name'),
                  LABEL(T('БИК')), INPUT(_name='bik'),
                  LABEL(T('СЧЕТ')), INPUT(_name='acc'),
                  LABEL(T('ТРАНЗ.№')), INPUT(_name='tr_id'),
                  LABEL(T('ТРАНЗ.ДАТА')), INPUT(_name='tr_date'),
                  LABEL(T('код программы')), SELECT(*[OPTION('%s [%s]' % (r.fonds.cod, r.goods.ab), _value = r.fonds.id)
                      for r in db(db.fonds.good_id == db.goods.id).select()
                          if not r.fonds.stats and not r.fonds.closed and r.goods.ab == 'RUB'], _name='fond_in_id'), # только для рублей!
                  LABEL(T('Сумма, руб (Полную сумму платежа пишем)')), INPUT(_name='amo'),
                  LABEL('Из них 500р вычтется и положится в основной фонд'),
                  LABEL('Если пусто или 0 - то это ассоциативный пайщик - без вступления'),
                  DIV(LABEL(T('Юридическое имя')), INPUT(_name='y_name'), _id='y_name')
                ),
                _id='hidden1', _class='hidden'),
        INPUT(_value=T('Принять'), _type='submit', _id='submit', _class='hidden'),
        _action='#',
        )
    #print type(f)
    #for (k,v) in f.iteritems():
    #    print k,v
    if f.accepts(request,session):
        rec = db(db.members.email==request.vars.get('email')).select().first()
        if rec:
            response.flash = T('ОШИБКА: Пайщик с таким емайл уже есть!')
            db.rollback()
            return locals()
        rec = db(db.members_add5.email==request.vars.get('email')).select().first()
        if not rec:
            response.flash = T('ОШИБКА: Кандидат не найден по емайл')
            db.rollback()
            return locals()

        import fonds
        good = db(db.goods.name=='рубли').select().first() # в рублях

        bik = f.vars.pop('bik') # вырежем из списка это поле чтобы оно ошибку не давало при вводе
        acc = f.vars.pop('acc')
        tr_id = f.vars.pop('tr_id')
        tr_date = f.vars.pop('tr_date')
        fond_in_id = f.vars.pop('fond_in_id')
        amo_inv = amo = Decimal(f.vars.pop('amo') or 0) # сколько заплочено
        if amo <0: amo_inv = amo = 0
        memb_id = accept_rec(rec, f.vars)
        memb = db.members[ memb_id ]

        # запомним реквизиты банковского счета
        b_acc_id = fond_in = None
        if bik:
            stor = db((db.storages.key_name == 'bik')
                      & (db.storages.key_value == bik)).select().first()
            storage_id = stor and stor.id or db.storages.insert( key_name = 'bik', key_value = bik)
            b_acc_id = db.memb_accs.insert(member_id = memb_id, storage_id = storage_id, acc = acc )
        # тут может и без реквизитов - наличкой внести
        if amo>0:
            fond_in = db.fonds[ fond_in_id ] # в основной фонд общества
            if not fond_in:
                response.flash = 'fond not found or empty'
                db.rollback()
                return locals()
            # он что-то уже оплатил
            f_invite = db((db.f_invite.face_id == memb.face_id)
                      & (db.f_invite.minor != True)).select().first()
            if f_invite.inv > amo:
                # вступительный взнос не дотянул - ассоциативный оставим
                # нельзя таких принимать дальше так как путаница будет со вступительным взносом
                response.flash = 'вступительный внос не достаточен %s < %s' % (amo, f_invite.inv)
                db.rollback()
                return locals()
                amo_inv_calc = amo
                f_invite = db((db.f_invite.face_id == memb.face_id)
                          & (db.f_invite.minor == True)).select().first()
            else:
                memb.update_record( minor = False )
                # вступительный взнос учтем
                amo_inv_calc = f_invite.inv
                # определим сколько он как пай заплатил
                amo = Decimal(amo) - f_invite.inv
                fond = db.fonds[ settings.FOND_NEDELIM ]
                from_fond = db.fonds[settings.FOND_CALC_INV ]
                # из неделимого фонда делаем выплату этих бонусов - там должно быть больше всегда
                fonds.make_trans(db, settings, memb, storage_id, good, amo_inv_calc, amo_inv_calc,
                             fond, tr_id, 'invite', from_fond)

            if amo>0:
                # что-то сверху упало - занесем в базу
                fonds.make_trans(db, settings, memb, storage_id, good, amo, amo,
                             fond_in, tr_id, 'on invite')

        response.flash = 'Принят как %s! Внос в %s <- %sRUB' % (memb.minor and 'ассоциативный' or 'действительный', fond_in and fond_in.cod or '*', amo)
        res = accept_rec_mail(rec, locals())
        #return res # если надо показать письмо
    elif f.errors:
        response.flash = 'form has errors'
    return locals()

def pay():
    rec_id = request.args(0)
    rec = rec_id and db.members_add5[rec_id]
    #print 'pay', rec
    if not rec:
        #response.flash = T('Такой записи нет')
        redirect(URL('index'))

    minor = False ##not not rec.minor  # добавим тут отрицание чтобы от None отстроиться
    f_invite = db((db.f_invite.face_id == rec.face_id)
                  & ( db.f_invite.minor == minor)
                     ).select().first()
    if not f_invite:
        response.flash = T('Такой записи нет в таблице взносов')
        redirect(URL('index'))

    b_accs = db(db.b_accs).select()
    common.send_email_to_descr([rec.email, 'icreator@mail.ru'],'ИПО "Польза" прием в пайщики - данные внесены', None,
                   locals(),'invite/pay_email.html', response, settings)

    return locals()

def addr_check():
    addr = request.vars.get('a')
    rec = db(db.memb_x_accs.addr == addr).select().first()
    if rec: return T('ОШИБКА: уже используется!!!')
    return T('да')

def addrs():
    id = request.args(0)
    #print id
    rec = id and db.members_add5[id]
    #print rec
    if not rec:
        redirect(URL('index'))
    elif rec.locked:
        # если уже нельзя править
        redirect(URL('pay',args=[id]))
    addrs = request.vars.addrs
    form = None
    if addrs:
        # значит нажали в этой форме продолжить
        addrs = type(addrs) == type([]) and addrs or [addrs]
        i = 0
        #print addrs
        for a in addrs:
            if len(a) < 30: continue
            addr_rec = db(db.memb_x_accs.addr == a).select().first()
            if addr_rec:
                # такой адрес уже используется
                continue
            db.members_add_x.insert( ref_id = id, addr = a)
            i +=1
        if i or not rec.not_memb:
            # адреса закатали - закроем изменения в записи
            rec.update_record( locked = True)
            if not rec.not_memb:
                redirect(URL('pay',args=[id]))
            else:
                # сразу примем как ассоциативного
                memb_id = accept_rec(rec)
                memb = db.members[ memb_id ]
                amo = amo_inv = 0
                upd = {}
                res = accept_rec_mail(rec, locals())
                #return res
                response.flash = T('Вы приянты как ассоциативный пайщик')
                return locals()

        else:
            # это партнер без вступительного взноса и без адресов
            response.flash = T('Задайте хотя бы один адрес крипто-имущества - ведь Вы не собираетесь вступать в общество')
            pass


    f = db.faces[rec.face_id]
    form = FORM( LABEL(T('Ваш емайл:')), INPUT(_name='email', _value=rec.email, _readonly=True),
        LABEL(T('Дата рождения:')), INPUT(_name='b_date', _value=rec.b_date, _readonly=True),
        LABEL(T('Тип лица:')), INPUT(_name='face', _value=f.name, _readonly=True),
        #LABEL(T('Тип пайщика:')), INPUT(_name='pp', _value=rec.minor and T('Ассоциативный') or T('Действительный'), _readonly=True),
        #readonly=True,
        )

    return locals()

def valid_email(form):
    if db(db.members.email==form.vars.email).select():
        form.errors.email = T('Такой емайл уже добавлен в пайщики')
        
#@cache.action(time_expire=3600, cache_model=cache.ram, vars=False, public=True, lang=True)
def index():
    id = request.args(0)
    rec = id and db.members_add5[id]
    if rec and rec.locked:
        # если уже нельзя править
        redirect(URL('pay',args=[id]))


    form = SQLFORM( db.members_add5, rec,
        )

    if request.cookies.has_key('gift_code'):
        # если есть скрытый код приглашения - вставим его
        gift_code = request.cookies['gift_code'].value
        form.vars['inv_cod'] = gift_code

    if form.process(keepvalues=True, onvalidation=valid_email).accepted:
        response.flash = T('Данные для %s сохранены...') % form.vars.email
        redirect(URL('addrs',args=[form.vars.id]))
    if form.errors:
        response.flash = T('Исправьте ошибки в форме')

    return locals()
