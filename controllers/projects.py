# coding: utf8
# try something like
def index():
    t = db((db.projects.hidden==None)
           | (db.projects.hidden==False)).select()
    return locals()
