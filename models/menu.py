import common

response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%(author)s <%(author_email)s>' % settings
response.meta.keywords = settings.keywords
response.meta.description = settings.description

is_mobile= request.user_agent().get('is_mobile')

#progs = []
#for pr in db(db.progs).select(orderby=db.progs.name):
#    progs.append((T(pr.name), False, URL('progs', 'index', args=[pr.id])))
#progs.append((B(T('Статистика')), False, URL('transs', 'index', args=['fonds'])))
#pr = db.progs[4]
#progs.append((B(T('Программа "Вклад 37,77%"')), False, URL('progs', 'index', args=[4])))
#progs.append((T('все'), False, URL('progs', 'index', args=[11])))

# мобильная версия - меню в один ряд!
response.menu = [
    (T('Начало'), True, URL('default','index'), # ОБЫЧНАЯ версия
     [(T('О нас'), True, URL('default','about')),
      (T('О выгоде'), True, URL('default','profit')),
      (T('О технологии блокчейн'), True, URL('default','index')),
      (T('Наши проекты'), True, URL('projects','index')),
      (T('Участники'), True, URL('membs','list'), [
        (T('Совет Общества'),False, URL('membs','list_mn', args=[1])),
        (T('Правление Общества'),False, URL('membs','list_mn', args=[2])),
        (T('Ревизионная комиссия'),False, URL('membs','list_mn', args=[3])),
        (B(T('Пайщики')),False, URL('membs','list')),
        (T('Ассоциативные пайщики'),False, URL('membs','list', args=[1])),
        (T('Публичные адреса'),False, URL('membs','addrs')),
        ]),
      #(T('Задачи'), False, None, [
      #  (T('Запустить программы'), False, URL('default','tasks1')),
      #  (T('Создать logo'), False, URL('default','logo')),
      #  (T('Прочие'), False, URL('default','tasks2')),
      #  ]),
      (T('Документы'), True, URL('default','docs')),
      (T('Контакты'), True, URL('default','conts')),
      (T('Новости, События'), True, URL('news','index')),
      ]
     ),
#(T('Probe'),False, URL('default','caroptions')),
(B(T('Выгоды для Вас')), True, URL('progs', 'index'), None),
(B(T('Выгоды для бизнеса')), True, URL('projects', 'index'), None),
(T('Вступить'), False, URL('invite','index'), not common.not_is_local() and [(T('Принять'), False, URL('invite','accept'))]),
(T('Учёт и статистика'), True, URL('transs','index'),
        not common.not_is_local() and
             [(T('Взнос на счет в банке'), False, URL('transs', 'fiat')),
             (T('Крипта'), False, URL('transs', 'crypto')),
             (T('Вещь'), False, URL('transs', 'item')),
             (T('Пересчет по всем транзакциям'), False, URL('tools', 'resum_ALL')),
             ]
        or []
    ),
#(B(T('#')), True, URL('shop', 'index'), [
#    (B(T('P')), True, URL('shop', 'prod'), None),
#    (B(T('C')), True, URL('shop', 'cate'), None),
#    ]),
]

# функция для рекурсии
def deep(tab, menu, pris):
    if type(menu) != type([]):
        if len(menu) > 2 and menu[2]:
            #print 'APPEND', menu
            tab.append((XML('%s%s' % (pris, menu[0])), menu[1], menu[2]))
        if len(menu) > 3 and menu[3]:
            deep(tab, menu[3], '%s%s.' % (pris, menu[0][:6]))
        return
    for i in menu:
        deep(tab, i, pris)
#
# если мобильная версия то все пункты меню со ссылками в простой список записывает
#
if is_mobile:
    tab = []
    deep( tab, response.menu, '' )
    response.menu = tab

response.menu_footer = [
    (T('Польза для Бизнеса'), False, URL('projects','index')),
    (T('Польза для Общества'), False, URL('social','roi')),
    (T('Управление паями'), False, URL('progs','fond')),
    (T('Работа'), True, URL('vacs','index')),
    (T('Новости, События'), True, URL('news','index')),
    (T('Обсуждения, форумы'), True, URL('more','talks')),
]
