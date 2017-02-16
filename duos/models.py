#coding:utf-8

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import random

# Create your models here.

choice = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'


def createRandomFields(size):
    ret = []
    for i in xrange(size):
        ret.append(random.choice(choice))
    return ''.join(ret)


class Account(models.Model):
    account_email = models.EmailField(unique=True)
    account_name = models.CharField(max_length=30)
    account_phone = models.CharField(max_length=11)

    def __str__(self):
        return "%s | %s" %(self.account_email,self.account_name)

class Application(models.Model):
    sKey = models.CharField('Secret Key',max_length=40)
    iKey = models.CharField('Integration Key',max_length=20)
    name = models.CharField(max_length=30)
    api_hostname = models.CharField(max_length=8,unique=True)
    account = models.ForeignKey(Account,on_delete=models.CASCADE)

    def __str__(self):
        return "%s | %s" % (self.name,self.api_hostname)

    @classmethod
    def new_app(self):
        '''
        返回一个参数字典，包含随机生成的sKey,iKey和hostname
        '''
        sKey = createRandomFields(40)
        iKey = createRandomFields(20)
        api_hostname = createRandomFields(8)
        while len(Application.objects.filter(api_hostname=api_hostname))>0:
            api_hostname = createRandomFields(8)
        ret = {
            'sKey':sKey,
            'iKey':iKey,
            'api_hostname':api_hostname
        }
        return ret
        

class User(models.Model):
    user_name = models.CharField(max_length=30,unique=True)
    user_phone = models.CharField(max_length=11)
    application = models.ForeignKey(Application,on_delete=models.CASCADE)

    def __str__(self):
        return "%s" %(self.user_name)




