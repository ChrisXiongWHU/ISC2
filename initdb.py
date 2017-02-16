#coding:utf-8

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whu_isc.settings")
import django
django.setup()

from duos.models import Account,Application,User,createRandomFields
from duos.tests import initdb,getSig,getSigNoUser
from django.urls import reverse





if __name__ == '__main__':
    #清空数据库表
    Account.objects.all().delete()
    Application.objects.all().delete()
    User.objects.all().delete()
    # acc,app,user,req,sig = getSigNoUser()
    acc,app,user,req,sig = getSig()
    parent = reverse('duos:test_response')
    sigS = 'http://127.0.0.1:8000/api-%s/frame/auth/?tx=%s&parent=%s' %(app.api_hostname,req,'http://127.0.0.1:8000'+parent)
    print sigS
    with open('sig.txt','w') as f:
        f.write(sigS)

  