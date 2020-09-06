# coding: utf8

import common, datetime

time_expire3600 = request.is_local and 3 or 3600
time_expire30 = request.is_local and 3 or 30

### required - do no delete
#def user(): return dict(form=auth())
def download(): return response.download(request,db)
#def call(): return service()
### end requires

@cache.action(time_expire=time_expire3600, cache_model=cache.ram, vars=True, public=True, lang=False)
def send_info():
    id = request.args(0)
    rec = id and db.members[id]
    goods = db(db.memb_goods.memb_id == rec.id ).select()
    goods_tab = [[T(''), DIV(T('Размер'), _class='middle'), T('Эквивалент')]]
    for r in goods:
        goods_tab.append([
            db.goods[r.good_id].name,
            r.amo,
            r.amo_out]
            )
    goods = TABLE(*[TR( *r) for r in goods_tab])
    #tab = TABLE(*[TR( *rows) for rows in tt])
    #fonds = db
    to_html = False
    #common.send_email_to_descr([rec.email, 'icreator@mail.ru'],'ИПО "Польза" - данные', None,
    #   rec,'membs/send_info.html', response, settings)
    #to_html = True
    return locals() #response.render('membs/accept_email.html',locs)

def addrs_get():

    xaddr = db(db.memb_x_accs.addr==request.vars.get('a')).select().first()
    rec = xaddr and db.members[xaddr.member_id]
    if rec:
        #fio = common.membr_fio(rec)
        # если на выходе Аякса ставить :eval то да но тт все проще
        #rec = "jQuery('#hidden').fadeOut('1755'); jQuery('#submit').fadeOut('755'); jQuery('#targ').html('%s')" % fio

        res = common.membr_uri(rec)
    else:
        # если на выходе Аякса ставить :eval то да но тт все проще
        # rec = "jQuery('#targ').html('%s')" % T('Не найден')
        res = T('Не найден')
    return res

# публичные адреса, по которым можно сказать кто есть кто
@cache.action(time_expire=time_expire30, cache_model=cache.ram, vars=True, public=True, lang=False)
def addrs():
    session.forget(response)
    response.title = T('Просмотр публичных адресов.')
    response.subtitle = T('Здесь Вы сможете узнать кому принадлежит тот или иной адрес крипто-имущества.')
    addrs = request.args(0) or request.vars.get('a')
    f = FORM(LABEL(T('Задайте адрес крипто-имущества')), INPUT(_name='a', _value = addrs or ''),
            INPUT(_value=T('Найти'), _name='check', _type='button',
            # jQuery(this).parent().html('%s')" % IMG(_src=URL('static','images/loading.gif'), _width=64)
            _onclick="jQuery('#targ').html('%s'); ajax('%s', ['a'], target='targ')"
                        % (IMG(_src=URL('static','images/loading.gif'), _width=28), URL('addrs_get'))),
            BR(),DIV(_id='targ'),
            )
    return locals()

@cache.action(time_expire=time_expire3600, cache_model=cache.ram, vars=False, public=True, lang=True)
def index():
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire3600)
    return dict()

def lst_0(v):
    if v:
        t = db((db.members.minor==True)
              ).select(orderby=db.members.l_name|db.members.f_name|db.members.m_name)
    else:
        # так как там и None
        t = db(~(db.members.minor==True)
              ).select(orderby=db.members.l_name|db.members.f_name|db.members.m_name)

    bal = MENU([(T('Взнос'),False, '', [(XML(T('Это возвращаемые<br>взносы')),False, '')]) ], _class='nav', li_class='dropdown',ul_class='dropdown-menu', mobile=False)
    bal_u = MENU([(T('[Взнос*]'),False, '', [(XML(T('Это невозвращаемые<br>взносы')),False, '')]) ], _class='nav', li_class='dropdown',ul_class='dropdown-menu', mobile=False)
    bal_c = MENU([(T('[Взнос**]'),False, '', [(XML(T('Сумма для расчета<br>кооперативных выплат')),False, '')]) ], _class='nav', li_class='dropdown',ul_class='dropdown-menu', mobile=False)
    #bal = ABBR(T('Взнос'), _title=T('Это возвращаемые зносы'))
    #bal = XML('<abbr title="' + T('Это возвращаемые взносы') + '">' + T('Взнос') + '</abbr>')
    tt = [[T('ФИО'), bal, bal_u, bal_c]]
    for r in t:
        #tt.append(dict(mn='', l_name=r.l_name, f_name=r.f_name,
        #    m_name=r.m_name or '', bal = r.bal, email= r.email, id=r.id)
        #    )
        if r.date_end: continue

        tt.append([ common.membr_uri(r),
                   r.bal, r.bal_u, r.bal_c,
                   #r.email,
                   ])
    tab = TABLE(*[TR(*rows, _class='gray1') for rows in tt],  _style='border-collapse:inherit; border-spacing: 0em 5px;')
    return tab

# тут быстро может инфо поменяться
@cache.action(time_expire=time_expire30, cache_model=cache.ram, vars=True, public=True, lang=True)
def list():
    session.forget(response)
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire30)

    tt = title = None
    if len(request.args)==0:
        title = T('Список пайщиков с голосом')
        tt = lst_0 ( False )
    else:
        title = T('Список ассоциативных пайщиков')
        tt = lst_0 ( True )

    invs = db(db.members_add5).count()
    return locals()

def lst_1(tab):
    t = db((db[tab].mn_id == db.meet_names.id)
               & (db[tab].member_id == db.members.id)
                  ).select(orderby=db.meet_names.wei|db.members.l_name|db.members.f_name|db.members.m_name)
    #print t
    tt = []
    for r in t:
        if r.members.date_end: continue

        #print r.members.l_name, r.members.f_name
        tt.append( [
                       r.members.foto and IMG(_src=URL('membs','download', args=['db', r.members.foto]), _width=200) or '',
                       TD(r.meet_names.name + ': ',  _class='center'),
                       TD(common.membr_uri(r.members),  _class='center'),
                       TD(r.members.bal, _class='center'), TD(r.members.bal_u, _class='center'),
                       TD(r.meet_names.wei<'3' and r.members.email or '',  _class='center')
                       ]
            )
    #  _vertical_align='middle'),  _valign='middle'),
    tab = TABLE(*[TR(*rows, _class='gray1') for rows in tt], _style='border-collapse:inherit; border-spacing: 0em 1em;') #, _class='center')
    return tab

@cache.action(time_expire=time_expire30, cache_model=cache.ram, vars=True, public=True, lang=True)
def list_mn():
    session.forget(response)
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire30)

    sel = len(request.args)==0 and 2 or int(request.args[0])

    tt = title = None
    if sel == 2:
        title = T('Список Правления Общества')
        tt = lst_1('memb_meets')
    elif sel == 3:
        title = T('Список Ревизионной Комиссии Общества')
        tt = lst_1('memb_audits')
    else:
        title = T('Список Совета Общества')
        tt = lst_1('memb_cons')

    return locals()
