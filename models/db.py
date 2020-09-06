# -*- coding: utf-8 -*-
from decimal import Decimal
# fonds:
    #stats=db.fonds.calc
#    Field('stats', 'boolean', default=False, comment=T('для расчетов и статистики') ), #

# trans - get_info_last - storage_id
#
migrate=False
#migrate=True

if not DEVELOP:
    db = DAL("mysql://root:PASSWORD@localhost/polza1",
        #folder="applications/ipay9/databases",
        pool_size=2,
        migrate=migrate,
        #migrate_enabled=False,
        check_reserved=['all'],
        #fake_migrate_all=True,
        #auto_import=True, # это ключ благодаря которму не надо описывать таблицы заново тут
        )
else:
    db = DAL('sqlite://storage.sqlite',
        #folder="applications/ipay9/databases",
        migrate=True,
        #migrate_enabled=False,
        check_reserved=['all'],
        #fake_migrate_all=True,
        #auto_import=True, # это ключ благодаря которму не надо описывать таблицы заново тут
        )


#session.connect(request, response, db)

deb_cre = (
    Field('deb', 'decimal(23,8)', default=Decimal(0), comment='сколько пришло',
          readable=False, writable=False), # сколько всего в обществе
    Field('deb_out', 'decimal(23,8)', default=Decimal(0), comment='сколько пришло по курсу',
          readable=False, writable=False), # сколько всего в обществе
    Field('cre', 'decimal(23,8)', default=Decimal(0), comment='сколько ушло',
          readable=False, writable=False), # сколько всего в обществе
    Field('cre_out', 'decimal(23,8)', default=Decimal(0), comment='сколько ушло по курсу',
          readable=False, writable=False), # сколько всего в обществе
    )

##########################################
db.define_table('b_accs', # счета ПО в банках
    Field('unused', 'boolean', comment=T('блокированный')), #
    Field('bik', length=40, unique=False,
        requires = [IS_NOT_EMPTY()]),
    Field('acc', length=40, unique=False,
        requires = [IS_NOT_EMPTY()]),
    )

db.define_table('faces', # типы лиц - юр, физ, ИП и пр
    Field('name', length=60, unique=True, requires = [IS_NOT_IN_DB(db,'faces.name')]),
    Field('ab', length=6, unique=False, requires = [IS_NOT_IN_DB(db,'faces.ab')]),
    format='%(name)s',
    )
db.define_table('f_invite', # взносы вступительные и минимальные
    Field('face_id', db.faces),
    Field('minor', 'boolean', comment=T('Ассоциативный')), #
    Field('inv', 'decimal(10,2)', default=Decimal(0)),
    Field('min_', 'decimal(10,2)', default=Decimal(0)),
    )

def membs_frm(r):
    if r.y_name:
        return '%s %s' % (r.y_name, r.inn)
    else:
        dt = r.b_date and r.b_date.__format__('%m-%d') or '-'
        #print dt
        return '%s %s %s' % (r.l_name, r.f_name, dt)

db.define_table('members',
    Field('email', length=60, unique=True,
        requires = [IS_NOT_IN_DB(db,'members.email'), IS_EMAIL(error_message=T('invalid email!'))], readable=False, writable=True),
    Field('face_id', db.faces, label=T('Вид лица')),
    Field('f_name', length=30, label=T('Имя'), comment=T('Имя')), # Дмитрий first name
    Field('m_name', length=30, label=T('Отчество'), comment=T('Отчество')), # C
    Field('l_name', length=30, label=T('Фамилия'), comment=T('Фамилия')), # Ermolaev , required=True, requires=IS_NOT_EMPTY()
    Field('b_date', 'date', label=T('д.р.'), comment=T('дата рождения')),
    Field('y_name', length=100, label=T('Юр. Название'), comment=T('имя юр.лица')), # юридическое имя
    Field('OGRN', length=30, label=T('ОГРН'), readable=False, comment=T('ОГРН юр.лица')), # юридическое имя
    Field('addr', 'text', requires=IS_NOT_EMPTY(), readable=False, writable=True, comment=T('Место жительства, юр.адрес')), #
    Field('contacts', 'text', readable=False, writable=True, comment=T('Контакты, тел, скайп и пр.')), #
    Field('inn', length=40, readable=False, writable=True, comment=T('ИНН')), #
    Field('foto', 'upload', label=T('Фото'),
          requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png'), maxsize=(1300, 1800)))),
    Field('prt_cod', length=10, comment=T('Код партнера'), readable=False, writable=False), #
    Field('inv_id', 'reference members', readable=False, writable=True, comment=T('ИД - пригласившего')), #
    Field('minor', 'boolean', default=False, comment=T('Ассоциативный?'), readable=True, writable=False, ), #
    # это чисто статистика в рублях фондов, реальные паи в имуществе хранятся
    Field('bal', 'decimal(23,2)', label=T('Взносы'), default=Decimal(0), readable=True, writable=False, comment='Возвращаемые взносы'),
    Field('bal_u', 'decimal(23,2)', label=T('Взносы*'), default=Decimal(0), readable=True, writable=False, comment='Невозвращаемые взносы'),
    Field('bal_c', 'decimal(23,2)',  label=T('Взносы**'),default=Decimal(0), readable=True, writable=False, comment='сумма взносов для расчета корпоративных выплат - расчет по коэфф. фондов'),
    Field('date_beg', 'date', label=T('Дата вступл.'),
          writable=False,  default=request.now, comment='дата входа'  ),
    Field('date_end', 'date', label=T('Дата выхода'),
          writable=False, comment='дата выхода' ),
    format=membs_frm,
    singular=T('Пайщик'), plural=T('Пайщики'),
    )
db.define_table('meet_names', # Правление
    Field('wei', length=1), # вес должности
    Field('name', length=30), # должность
    format='%(wei)s - %(name)s',
    )
db.define_table('memb_cons', # Совет
    Field('member_id', 'reference members', readable=False, writable=False), # reference db. - отключаени линки в smart.grid и в ДБ админки
    #Field('member_id', db.members), #
    Field('mn_id', db.meet_names), #
    singular=T('Совет'), plural=T('Совет'),
    )
db.define_table('memb_meets', # Правление
    Field('member_id', 'reference members'),
    #Field('member_id', db.members), #
    Field('mn_id', db.meet_names), #
    singular=T('Правление'), plural=T('Правление'),
    )
db.define_table('memb_audits', # Ревизия
    Field('member_id', 'reference members'),
    #Field('member_id', db.members),
    Field('mn_id', db.meet_names),
    singular=T('Ревизия'), plural=T('Ревизия'),
    )


##############################################
#  это общая база для хранилищ имущества ЕГРЙ, банки, биткоин, ЯДеньги и пр
#  первая запись - пусто
# сюда писать только то что может быть множественным по отношению к одному имуществу
# например деньги, акции, металлы можно хранить в разных банках - вот банки сюда и катаем
# ЯДеньги, биткоины - можно хранить только в одном хранилище - сюда не катаем
###
db.define_table('storages',
    Field('name', length=100),
    Field('url', length=100),
    Field('key_name', length=10), # уникальный ключ - типа БИК или СВИФТ или еще чего
    Field('key_value', length=40), # уникальный ключ - типа БИК или СВИФТ или еще чего
    Field('addr', 'text'),
    format='%(name)s %(key_value)s',
    )
st = db(db.storages).select().first
if not st:
       db.storages.truncate()
       db.storages.insert( name = '.nil.' )

db.define_table('memb_accs', # счета в хранилищах членов
    Field('member_id', db.members),
    Field('storage_id', db.storages, default=1),
    Field('acc', length=50, unique=False ),
    singular=T('Счет'), plural=T('Счета'),
    )
db.define_table('memb_x_accs', # Крипто-Адреса членов
    Field('member_id', db.members),
    Field('addr', length=140, unique=True,
        requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db,'memb_x_accs.addr')]),
    singular=T('Крипто.адрес'), plural=T('Крипто.адреса'),
    )

# новый член - все остальное берется из платежа
db.define_table('members_add5',
    Field('email', length=60, unique=False,
        requires = [
            IS_NOT_IN_DB(db,'members_add5.email'),
            IS_EMAIL(error_message=T('invalid email!')),
            ],
        readable=True, writable=True,
        comment='',
        ),
    Field('b_date', 'date', requires=IS_NOT_EMPTY(),
          label=T('Дата рождения (ГГГГ-ММ-ЧЧ):'),
          readable=False, writable=True,
          ),
    Field('prt_cod', length=8, comment=T('Код партнера'), readable=False, writable=False), #
    Field('inv_cod', length=10, label=XML(T('Код пригласившего Вас пайщика<BR>(он же "подарочный код")')),
          readable=False, writable=True, comment='.'), #
    Field('face_id', db.faces, label=T('Вид лица'), default=1, comment='.'),
    Field('not_memb', 'boolean', label=T('Не как пайщик'),  readable=True, writable=True, comment=T('Без вступительного взноса сейчас - я регистрируюсь только для партнерской программы. Возможно потом вступлю оплатив вступительный взнос...') ),
    Field('locked', 'boolean',  readable=False, writable=False, comment=T('Если залочен то нельзя уже менять') ),
    #Field('minor', 'boolean', readable=False, writable=False,
    #      label=T('Ассоциативный пайщик'), comment=T('Поставив галочку Вы вступаете как ассоциативный пайщик, который не имеет голоса на собраниях, не может быть избран в Правление и Ревизионную комиссию общества, не отвечает субсидиарно по долгам общества, но за то, имея все остальные права обычного пайщика не обязан оплачивать минимальный паевой взнос.')), #
    format='%(email)s',
    #redefine=True,
    )
db.define_table('members_add_x',
    Field('ref_id', db.members_add5),
    Field('addr', length=140, label=T('Адрес крипто-имущества (длинна более 30 знаков)'), writable=False, readable=True,
          comment=T('укажите адрес Вашего кошелька')),
    )


db.define_table('goods_cat0',
    Field('name', length=40),
    Field('ab', length=10),
    format='%(ab)s',
    )

db.define_table('props', # свойства вещей
    Field('name', length=40),
    Field('ab', length=10),
    format='%(name)s',
    )
db.define_table('units', # единицы измерения
    Field('prop_id', db.props), # для какого свойства подходит
    Field('name', length=40),
    Field('ab', length=10),
    format='%(ab)s',
    singular=T('Еденица'), plural=T('Единицы'),
    )

def goods_cat1_f(r):
    c = db.goods_cat0[r.ref_id]
    return '%s.%s' % (c.ab, r.ab)
db.define_table('goods_cat1',
    Field('ref_id', db.goods_cat0),
    Field('name', length=40),
    Field('ab', length=10),
    Field('prop_id', db.props), # главное свойство вещей данной категории
    format=goods_cat1_f,
    )

#db.goods_cat1.ref_id.widget = SQLFORM.widgets.autocomplete(
#     request, db.goods_cat0.name, limitby=(0,10), min_length=2, id_field = db.goods_cat0.id )
#db.goods_cat1.ref_id.widget = SQLFORM.widgets.optopns()
db.define_table('goods',
    Field('ref_id', db.goods_cat1, label=T('Категория')),
    Field('name', length=40, label=T('Название')),
    Field('ab', length=10, label=T('Сокр.')),
    Field('its_unit', 'boolean', label=T('ед. изм.'), comment='это еденица измерения сама'), # значит свойства тут не учитываются
    Field('prop1_value', 'decimal(23,8)', default=Decimal(0),
          label=T('Знач. свойства1'), comment='значение первого свойста по категории вещей'), #
    Field('prop1_unit', db.units, default=1, label=T('ед. изм.')), # едница измерения значения
    Field('prop2_id', db.props, default=1, label=T('Имя доп. свойства')), # дополнительное свойство
    Field('prop2_value', 'decimal(23,8)', default=Decimal(0),
          label=T('Значение'), comment='значение второго свойста по категории вещей'), #
    Field('prop2_unit', db.units, default=1, label=T('ед. изм.')), # едница измерения значения
    Field('info', 'text', label=T('Описание')),
    Field('amo1', 'decimal(23,8)', default=Decimal(1), comment='сколько у 1штуки'), # сколько у 1штуки
    Field('amo', 'decimal(23,8)', default=Decimal(0), comment='сколько в обществе'), # сколько всего в обществе
    Field('amo_out', 'decimal(23,8)', default=Decimal(0), comment='сколько в обществе по курсу единиц фондов'), # сколько всего в обществе
    *deb_cre,
    format='%(name)s',
    singular=T('Вещь'), plural=T('Вещи')
    )
# курсы для ВЕЩЕЙ
# запоминаем при появлении транзакций
# или задаем вручную
db.define_table('good_rates',
    Field('ref1', db.goods),
    Field('ref2', db.goods),
    Field('buy', 'float', default=0.0), #
    Field('sell', 'float', default=0.0), #
    Field('on_create', 'datetime', writable=False,  default=request.now ),
    )

################################################################################
################################################################################
# проекты наши, те что в общем котреле
db.define_table('projects',
    Field('hidden', 'boolean', comment='Программа закрыта'),
    Field('cod', length=10),
    Field('name', length=70),
    Field('info', 'text'),
    Field('status', length=40),
    Field('url', length=40),
    format='%(cod)s',
    )
db.define_table('progs',
    Field('hidden', 'boolean', comment='не показывать!'),
    Field('closed', 'boolean', comment='Программа закрыта'),
    Field('promo', 'boolean',  readable=False, writable=False, comment=T('их выставляем на показ везде') ),
    Field('cod', length=10),
    Field('name', length=40),
    Field('info', 'text'),
    Field('bal', 'decimal(23,2)', default=Decimal(0), readable=False, writable=False), # пай возвращаемый
    Field('bal_u', 'decimal(23,2)', default=Decimal(0), readable=False, writable=False),
    *deb_cre,
    format='%(cod)s'
    )

def fonds_frm(r):
    #rr = db.progs[r.prog_id]
    return r.cod + ':' + r.name
db.define_table('fonds',
    Field('prog_id', db.progs, label=T('Код прогр.')),
    Field('wei', length=2, readable=False), # вес рекламе
    Field('stats', 'boolean', default=False, comment=T('для расчетов и статистики') ), #
    Field('unret', 'boolean', comment='Невозвращаемые взносы'),
    Field('closed', 'boolean', comment='Прием взносов закрыт'),
    Field('name', length=40, label=T('Название')),
    Field('cod', length=10, label=T('Код')),
    Field('info', 'text', label=T('Описание')),
    Field('koef', 'decimal(4,2)', default=Decimal(1), label=T('Коэф.'), comment='Коэффициент увеличивающий взносы'),
    # если фонд рублевый чисто то все поступления конвертируем
    # иначе храним как - чем платили и пересчет пая по курсу каждый день
    Field('good_id', db.goods, label=T('Вещь учета'), comment='Если задан вид имущества фонда то все взносы конвертируем в него'),
    Field('cp_pars', 'json', comment='доп. параметры для криптоПай - например прием только в заданной крипте {"curr_in":"BTC"}', readable=False, writable=False),
    Field('bal', 'decimal(23,2)', default=Decimal(0), label=T('Баланс')),
    *deb_cre,
    format=fonds_frm, #'%(prog_id)s: %(name)s',
    singular=T('Фонд'), plural=T('Фонды')
    )
# тут поидее алгоритм автоматических начислений для данного фонда
# тут может быть несколько авторасчетов для одного фонда
# ВНИМАНИЕ если фонд не задана валюта то тут нельзя задавать vol vol_a
db.define_table('fond_calcs',
    Field('fond_id', db.fonds, comment='По этому фонду смотрим величину поступления для вычисления %-в'),
    Field('perc', 'decimal(4,2)', default=Decimal(1), comment='процент бонуса, 1.00 = 1%'),
    Field('vol', 'decimal(10,2)', default=Decimal(0), comment='!!!Внимание!!! может быть задано только для фондов с заданной валютой так как иначе не понятно в чем выдавать сумму. Если задан процент - то это максимальное значение его. иначе это абсолютное значение награды'),
    #Field('perc_a', 'decimal(4,2)', default=Decimal(1), comment='для ассоц.пайщика процент бонуса, 1.00 = 1%'),
    #Field('vol_a', 'decimal(10,2)', default=Decimal(0), comment='для ассоц.пайщика '),
    Field('self_', 'boolean', comment='Это начисление для того же пайщика, иначе - награда для его партнера'),
    Field('lvl_div', 'integer', default=3, comment='делитель на уровень'),
    Field('lvl_max', 'integer', default=5, comment='глубина уровеней'),
    Field('from_fond_id', db.fonds),
    Field('to_fond_id', db.fonds),
    )

###################################################################################
# какое имущество в каком кол-ве в какой фонд пришло и от кого
###################################################################################
##### это основа инфо всей - на базе нее все расчеты можно переделывть
# на основании этого вся инфо везде по фондам меняется
# поидее тут проводки должны быть от реквизитом платежа выдавать пайщика
# минус в количестве - уход
args1 = (
    # откуда транзакция пришла
    Field('storage_id', db.storages, default=1, label=T('Хранилище вещей'),
          comment='Имя_Банк? биткоин? ЯДеньги? Фирма_по_договору? короче откуда по номеру транз можно всю инфо получить'),
    Field('from_fond_id', db.fonds, label=T('Из фонда'), comment='из фонда'), # из какого фонда
    Field('fond_id', db.fonds, label=T('В фонд'), comment='в фонд'), # в какой фонд
    Field('good_id', db.goods, label=T('Вещи')), # вид+тип имущества - вещь
    Field('memb_id', db.members, label=T('Пайщику')),
    # квартииа, автомашина - штуками,хотя и доли тоже могут быть
    Field('amo', 'decimal(23,8)', default=Decimal(0), label=T('Сколько')),
    Field('amo_out', 'decimal(23,8)', default=Decimal(0),
          label=T('Сколько в ед. учета')), # курс обмена крипты на фиат или еще чего который в криптоПай был взят
    Field('on_create', 'datetime', label=T('создано'), writable=True,  default=request.now ),
    Field('txid', length=80, comment='txid-vout'), # сюда вкаываем номер транзакции +ВОУТ ...465-001 или номе ьанкаовской транз
    Field('info', 'text', label=T('Инфо'), comment=T('доп. информация'), readable=True, writable=True), # сюда  закатываем всю прочую инфо по транзакции
    )

### в транзакциях нет оборотов
####args1 = args1 + deb_cre

vars1 = dict(
    singular=T('Транзакция'), plural=T('Транзакции'),
    )

db.define_table('trans',
    Field('calced', 'boolean',
          label=T('Выч.'), comment='это вычисленная транзакция - их удаляем при полном пересчете'),
    *args1,
    **vars1
    )
db.define_table('trans_calc',
    Field('ref_', db.trans),
    *args1,
    **vars1
    )
# какое имущество в каком кол-ве есть у какого пайщика
db.define_table('memb_goods',
    Field('memb_id', db.members),
    Field('good_id', db.goods),
    # квартииа, автомашина - штуками,хотя и доли тоже могут быть
    Field('amo', 'decimal(23,8)', default=Decimal(0)),
    Field('amo_out', 'decimal(23,8)', default=Decimal(0)), # сколько всего в обществе
    *deb_cre,
    singular=T('Вещи пайщика'), plural=T('Вещи пайщиков')
    )
# какое имущество в каком кол-ве есть у кого фонда
db.define_table('fond_goods',
    Field('fond_id', db.fonds),
    Field('good_id', db.goods),
    # квартииа, автомашина - штуками,хотя и доли тоже могут быть
    Field('amo', 'decimal(23,8)', default=Decimal(0)),
    Field('amo_out', 'decimal(23,8)', default=Decimal(0)), # сколько всего в обществе
    *deb_cre,
    singular=T('Вещи фонда'), plural=T('Вещи фондов')
    )
# какое имущество в каком кол-ве есть у кого фонда
db.define_table('fond_memb_goods',
    Field('fond_id', db.fonds),
    Field('memb_id', db.members),
    Field('good_id', db.goods),
    # квартииа, автомашина - штуками,хотя и доли тоже могут быть
    Field('amo', 'decimal(23,8)', default=Decimal(0)),
    Field('amo_out', 'decimal(23,8)', default=Decimal(0)), # сколько всего в обществе
    *deb_cre,
    singular=T('Вещи фонда-пайщика'), plural=T('Вещи фондов-пайщиков')
    )


# номера счетов в криптопае
db.define_table('orders',
    Field('name', length=20),
    Field('bill', 'integer'),
    Field('fond_id', db.fonds),
    Field('last_dt', 'datetime' ), # с какой даты читать проводки по счету из криптопая
    Field('amo_hard', 'decimal(23,8)', default=Decimal(0))
    )

# обработанные транзакции из криптопая
db.define_table('order_txids',
    #Field('order1_id', db.orders),
    Field('order_id', db.orders),
    #Field('order_id', 'reference orders'),
    Field('txid', length=80),
    redefine=True,
    )

db.define_table('logs',
    Field('on_create', 'datetime', writable=False,  default=request.now ),
    Field('ccc', length=10),
    Field('fff', length=10),
    Field('messages123456', 'text'),
    )
db.define_table('file_hashes',
    #Field('file', 'upload', requires = IS_EMPTY_OR(IS_IMAGE(extensions=('jpeg', 'png'), maxsize=(900, 800)))),
    Field('good', 'upload', requires = [IS_NOT_EMPTY(),IS_LENGTH(10485760, 1024)]),
    Field('sha256', length=124),
    Field('addr', length=66),
    )
db.define_table('news',
    Field('on_create', 'datetime', writable=False,  default=request.now ),
    Field('ev', 'datetime', writable=False,  default=request.now, comment='когда будет событие' ),
    Field('hd'),
    Field('ur', comment='URL'),
    Field('tx', 'text'),
    )
#
# временная таблица для посланных команд
db.define_table('cmds',
    Field('name', length=15),
    Field('hash1', 'integer'),
    Field('pars', 'json'),
    Field('created_on', 'datetime', default=request.now),
    Field('status', length=3),
    Field('res', 'json'), # ответ от сервиса
    Field('res_on', 'datetime'),
    )
db.define_table('cmds_stack',
    Field('ref_', db.cmds),
    Field('hash1', 'integer'),
    )
