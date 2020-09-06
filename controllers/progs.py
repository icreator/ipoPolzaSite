# coding: utf8
import datetime

from gluon.tools import fetch

import common

class Jammer():
   def read(self,n): return 'x'*n
def jam(): return response.stream(Jammer(),40000)

res = []
def r(*pars):
    res.append(CAT(pars))

# тут быстро может инфо поменяться
time_expire = 30

def make_fond_make_url(f, pars):
    url_vars = settings.CP_URL_VARS.copy()
    url_vars['order'] = f.cod
    if f.cp_pars:
        url_vars.update(f.cp_pars)
    #print url_vars, pars
    url_vars.update(pars)
    return URL(*settings.CP_URL_MAKE, vars=url_vars, **settings.CP_URL_PARS)

# создаем сылку
def make_fond_show_url(f, pars={}, order=None):
    order = order or db(db.orders.fond_id == f.id).select().first()
    if order and order.bill:
        cpay_bill_id = order.bill
    else:
        # нет еще счета - надо создать через make
        url = make_fond_make_url(f, pars)
        resp = fetch(url)
        # print resp
        try:
            # split bill_id and secret_key
            tab = resp.split('.')
            bill_id = tab[0]
            bill_id = int(bill_id)
            if len(tab)>1:
                secret_key = tab[1]
            cpay_bill_id = resp
        except:
            # something wrong
            return 'ERROR: %s' % resp

    if order:
        # обновим запись
        order.update_record(bill = cpay_bill_id )
    else:
        # создадим запись
        #print 'update order_rec with', resp
        # save response as [bill_id].[secret_key] in order record
        order_id = db.orders.insert(fond_id = f.id, name = f.cod, bill = cpay_bill_id )
    #db.commit()


    return settings.CP_URL_SHOW + ('%s' % cpay_bill_id)

def fond():
    id = request.args(0)
    if id and not id.isdigit():
        return jam()

    f = db.fonds[ id ]
    if not f:
        response.flash = T('Выберите Фонд')
        for f in db(db.fonds).select(orderby=db.fonds.cod):
            if f.stats: continue
            r(A(f.name, _href=URL('progs','fond',args=[f.id])), BR())
        return dict(res=DIV(res))
    p = db.progs[f.prog_id]
    r(H3(f.name), f.info, A(H4(T('Программы %s') % p.name), _href=URL('progs','index',args=[p.id])), BR())
    if f.stats:
        pass
    else:
        url = make_fond_show_url( f )
        r(DIV(CAT(T('Оплатить взнос в фонд'), BR(),
            A('криптоимуществом', _href=url, _target='_blank', _class='btn big_btn'),
            A('обычными деньгами (фиатом)', _href=URL('pay',args=[ f.cod]), _target='_blank', _class='btn big_btn'),
            BR()), _class='gray1'))
        cc = CAT(T('Подать заяку на возврат части взноса'), BR())
        url = URL('more','in_progress')
        if f.good_id:
            u = db.goods[f.good_id]
            cc += CAT(A(B(u.ab), _href=url, _target='_blank', _class='btn big_btn'),BR())
        else:
            for u in db(db.goods).select():
                cc += CAT(A(B(u.ab), _href=url, _target='_blank', _class='btn big_btn'),' ')
        r(DIV(cc, _class='gray1'))


    return dict(res=DIV(res))

@cache.action(time_expire=time_expire, cache_model=cache.ram, vars=True, public=True, lang=True)
def pay():
    session.forget(response)
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire)
    cod = request.args(0)
    if cod and not cod.isdigit():
        return jam()
    return locals()

def fond_calc_text(good, fond_calc):
    res1 = CAT(T('Если Вы являетесь пайщиком общества'), ':',BR())
    ul = []
    dd = CAT(T('За своих приглашенных'), ' ')
    if fond_calc.perc:
        #res1 = res1 + CAT(T(''),B(fond_calc.perc),'%')
        dd += CAT(B(fond_calc.perc),'%')
        if fond_calc.vol and good:
            dd += CAT(', ', T('но не более'),' ',fond_calc.vol, '[',good.ab,']', BR())
    elif good and fond_calc.vol:
            dd += CAT(B(fond_calc.vol),'[',good.ab,']', BR())
    else:
            dd += CAT('-')
    ul += LI(dd)
    ul += LI(CAT(T('За приглашенных вашими приглашенными:'),' ',
              XML(T('деление текущей награды на %s при максимальной глубине приглашения %s.') % (B(fond_calc.lvl_div), B(fond_calc.lvl_max)))))
    ul += LI(CAT(T('Если Вы являетесь ассоциативным пайщиком общества, то вознаграждение уменьшается в 2 раза.')))
    return UL(*ul)

#@cache.action(time_expire=time_expire, cache_model=cache.ram, vars=True, public=True, lang=True)
def index():
    cache_time = request.now
    dt_expire = datetime.timedelta(0, time_expire)

    fond_cod = request.vars.get('order')
    if fond_cod and not fond_cod.isdigit():
        return jam()

    if fond_cod:
        fond = db(db.fonds.cod == fond_cod).select().first()
        id = fond and fond.prog_id
    else:
        id = request.args(0)
        if id and not id.isdigit():
            return jam()

    prog = id and db.progs[id]
    fonds = prog and db(db.fonds.prog_id == id).select(orderby=~db.fonds.wei)

    if prog:
        if prog.hidden: return dict(res=DIV('not founded'))

        fond_calcs_mem = []
        r(
            H2('%s "%s"' % (T('Программа'), T(prog.name))),
            XML(prog.info),
            BR(),
            DIV(H4(CAT(T('Обязательно узнайте '),
                A(B(T('Общие правила для взносов в фонды')), _href=URL('progs','rules'), cid='rules'))), _id='rules'),BR(),
            T('Программа содержит фонды:'),
            )
        for f in fonds:
            cc = CAT(
                H3(T(f.name)),
                T('Описание'),': ',XML(f.info),BR()
                )
            if f.stats:
                cc += CAT(T('Поступило'), ': ',B(abs(f.bal)),BR())
            else:
                cc += CAT(T('Тип взносов'),': ',B(f.unret and T('Невозвращаемые взносы') or T('Возвращаемые взносы')),BR())
            cc += CAT(T('Код фонда'), ': ', B(f.cod), BR(),
                T('Имущество (валюта) учета взносов:'), ' ',
                )
            good = f.good_id and db.goods[f.good_id]
            if good:
                cc += CAT(B(good.name))
            else:
                cc += CAT(B('Взносы не конвертируются, хранятся в том в чем поступили в фонд.'))
            cc += CAT(BR())

            if f.koef and f.koef>1:
                cc += CAT(T('Увеличивающий коэффициент для взносов'),': ',B(f.koef), BR())
            if f.closed:
                cc += CAT(T('Платежи сейчас не принимаются либо начисляются автоматически.'))
            else:
                order = db(db.orders.fond_id == f.id).select().first()
                cp_bill_id = order and order.bill

                cc += CAT(A(B(T('Статистика оплат криптоимуществом')),
                            _href=settings.CP_URL_BILL_STATS + ('%s' % cp_bill_id), _target='_blank'), BR())
                cc += CAT(BR())

                url = make_fond_show_url( f, {}, order )
                cc += CAT(T('Оплатить взнос в фонд'), BR(),
                    A('криптоимуществом', _href=url, _target='_blank', _class='btn big_btn'),
                    A('обычными деньгами (фиатом)', _href=URL('pay',args=[ f.cod]), _target='_blank', _class='btn big_btn'),
                    )
            cc += CAT(BR())
            cc += CAT(A('Управление паями - вернуть, перевести', _href=URL('progs','fond',args=[ f.id]),  _class='btn big_btn'),BR())


            fond_calcs = db(db.fond_calcs.fond_id == f.id).select()
            if len(fond_calcs)>0:
                cc += CAT(T('За взносы в этот фонд ваших приглашенных начислются поощрения:'),BR())
                for fond_calc in fond_calcs:
                    if fond_calc.self_:
                        cc += CAT('SELF')
                    f_s = db.fonds[fond_calc.to_fond_id]
                    if f_s.prog_id == prog.id:
                        p_s_t = T('этой же програмы')
                        p_s_u = ''
                    else:
                        p_s_t = T('програмы')
                        prog_s = db.progs[f_s.prog_id]
                        p_s_u = A(B(prog_s.name), _href=URL(args=[prog_s.id]))
                    cc += CAT(T('в'),' ',B(f_s.name), ' ', p_s_t, ' ', p_s_u, BR())
                    good_s = common.get_bonus_good(db, good, fond_calc, f_s)
                    cc += fond_calc_text(good_s, fond_calc)
                    #fond_calcs_mem.append([fond_calc, f ])

            fond_calcs = db(db.fond_calcs.to_fond_id == f.id).select()
            if len(fond_calcs)>0:
                cc += CAT(T('В этот фонд начисляются поощрения за вклады ваших приглашенных:'),BR())
                for fond_calc in fond_calcs:
                    if fond_calc.self_:
                        cc += CAT('SELF')
                    f_s = db.fonds[fond_calc.fond_id]
                    if f_s.prog_id == prog.id:
                        p_s_t = T('этой же програмы')
                        p_s_u = ''
                    else:
                        p_s_t = T('програмы')
                        prog_s = db.progs[f_s.prog_id]
                        p_s_u = A(B(prog_s.name), _href=URL(args=[prog_s.id]))
                    cc += CAT(T('в'),' ',B(f_s.name), ' ', p_s_t, ' ', p_s_u, BR())
                    good_s = common.get_bonus_good_to(db, good, fond_calc, f_s)
                    cc += fond_calc_text(good_s, fond_calc)
                    #fond_calcs_mem.append([fond_calc, f_s ])

            cc += CAT(T('Собрано (начислено)'),': ',B(abs(f.bal)),BR())
            r(DIV(cc, _class='gray1'))

    else:
        r(
            H4(T('Польза для обычных граждан от участия в нашем инновационном потребительском обществе:')),
            DIV(CAT(UL(
                T('Более низкие цены при закупке товаров и услуг у фирм и предприятий, являющихся нашими пайщиками или нашими оптовыми поставщиками.'),
                T('Прибыль по итогам года от коммерческой деятельности общества.'),
                T('Вклады под выгодные проценты, намного превышающие банковский процент.'),
                T('Оплата крипто-имуществом услуг и товаров напрямую через нашу платежную систему.'),
                CAT(T('Для майнеров крипто-имущества:'),
                    UL(
                        T('Совместная покупка майнеров и добывающих мощностей оптом - что дешевле розницы.'),
                        T('Безналоговая очистка майнига - легализация добытого крипто-имущества по законам РФ без уплаты налогов.'),
                    )),
                ))),
            H4(T('Основные выгоды дают следующие программы:')))

        #for pr in db((db.progs.promo==True) & ~(db.progs.closed.belongs(None, False))).select():
        for pr in db((db.progs.promo==True) & ((db.progs.closed==False) | (db.progs.closed==None))
                    & ((db.progs.hidden==False) | (db.progs.hidden==None))).select():
        #for pr in db(db.progs.promo==True).select():
        #    if pr.closed: continue
            cc = CAT(H3(CAT(A(B(T(pr.name)), _href=URL('progs','index',args=[pr.id])))))
            cc += CAT(DIV(XML(pr.info)))
            cc += CAT(T('Собрано (начислено)'),': ',B(abs(pr.bal)), ' ', T('возвращаемых и'),' ',B(abs(pr.bal_u)),' ',T('невозвращаемых взносов'),BR())
            r(DIV(cc, _class='gray1'))
        r(BR())
        r(T('Так же юридические лица могут подключиться к '),A(B(T('нашим проектам')), _href=URL('projects','index')))
        r(H4(T('Кроме этого есть еще программы:')))
        #for pr in db((db.progs.promo.belongs(None, False)) & (db.progs.closed.belongs(None, False))).select():
        for pr in db((db.progs.hidden==False) | (db.progs.hidden==None)).select():
            if pr.promo or pr.closed: continue
            cc = CAT(H3(CAT(A(T(pr.name), _href=URL('progs','index',args=[pr.id])))))
            cc += CAT(DIV(XML(pr.info)))
            cc += CAT(T('Собрано (начислено)'),': ',B(abs(pr.bal)),' ',T('возвращаемых и'),' ',B(abs(pr.bal_u)),' ',T('невозвращаемых взносов'),BR())
            r(DIV(cc, _class='gray1'))
        r(H4(T('Закрытые программы:')))
        #for pr in db(~(db.progs.promo==True) & (db.progs.closed!=True)).select():
        for pr in db((db.progs.closed==True) & ((db.progs.hidden==False) | (db.progs.hidden==None))).select():
            cc = CAT(H3(CAT(A(T(pr.name), _href=URL('progs','index',args=[pr.id])))))
            r(DIV(cc, _class='gray1'))

    return dict(res=DIV(res))

@cache.action(time_expire=time_expire*10, cache_model=cache.ram, vars=False, public=True, lang=True)
# сдесь и так в теле функции ничего не вычисляется
# а рендеринг нужно кешировать через response.render(d)
def rules():
    return dict()
