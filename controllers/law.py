# coding: utf8

def index():
    h = CAT()
    h += A('Письмо №1 в ФНС об выборе вида имущества для учета биткоин', _href=URL('static','docs/law/btc-type.rtf'))
    return dict(h=h)
