from django.test import TestCase
from django.db import models

from .models import Account,Application,User,createRandomFields

from duo import _sign_vals,_parse_vals,sign_request
import random
from .duoTools import parseDuoSig,validateParams,checkUserEnrolled,signResponse
from pprint import pprint
from django.urls import reverse
import time


# Create your tests here.


def initdb():
    account1 = Account.objects.create(account_email='1050358918@qq.com', \
    account_name='chrisXiong',account_phone='15927432501')
    app1 = Application.objects.create(name='websdk1',account=account1,**Application.new_app())
    user1 = User.objects.create(user_name="xrb",user_phone="15927432501",application=app1)
    return account1,app1,user1
    
def getSig():
    account1,app1,user1 = initdb()
    aKey = createRandomFields(40)
    req = _sign_vals(app1.sKey,[user1.user_name,app1.iKey],'TX',300)
    sig = parseDuoSig(req)
    return account1,app1,user1,req,sig

def getSigNoUser():
    account1,app1,user1 = initdb()
    aKey = createRandomFields(40)
    req = _sign_vals(app1.sKey,['chris',app1.iKey],'TX',300)
    sig = parseDuoSig(req)
    return account1,app1,user1,req,sig



# class ModelsTest(TestCase):
#     def test_create_models(self):
#         account1 = Account.objects.create(account_email='1050358918@qq.com', \
#         account_name='chrisXiong',account_phone='15927432501')
#         app1 = Application.objects.create(name='websdk1',account=account1,**Application.new_app())
#         user1 = User.objects.create(user_name="xrb",user_phone="15927432501",application=app1)

# class DuoViewTest(TestCase):


#     def test_auth_pre(self):
#         acc,app,user,req,sig = getSigNoUser()
#         api_hostname = app.api_hostname
#         response = self.client.get(reverse('duos:pre_auth',args=(api_hostname,)),data={
#             'tx':req,
#             'parent':'http:123.123.132.132'
#         },follow=True)
#         print response
#         print response.redirect_chain
#         print User.objects.all()





class DuoToolsTest(TestCase):
    def testException(self):
        account1 = Account.objects.create(account_email='1050358918@qq.com', \
        account_name='chrisXiong',account_phone='15927432501')
        app1 = Application.objects.create(name='websdk1',account=account1,**Application.new_app())
        user1 = User.objects.create(user_name="xrb",user_phone="15927432501",application=app1)
        user2 = User.objects.create(user_name="xrb",user_phone="15927432501",application=app1)


    
#     def test_parse_duo_sig(self):

#         account1,app1,user1,req,sig = getSig()

#         self.assertEquals(sig['prefix'],'TX')
#         self.assertEquals(sig['content'][0],user1.user_name)
#         self.assertEquals(sig['content'][1],app1.iKey)
#         self.assertEquals(sig['sha_1'],req.split('|')[-1])
    
#     def test_validate_params_when_true(self):
#         account1,app1,user1,req,sig = getSig()
#         self.assertTrue(validateParams(sig,app1.iKey,app1.sKey))
    
#     def test_check_user_enrolled_when_true(self):
#         account1,app1,user1,req,sig = getSig()
#         self.assertIsNotNone(checkUserEnrolled(sig['content'][0],app1))
    
#     def test_check_user_enrolled_when_false(self):
#         account1,app1,user1,req,sig = getSig()
#         user2 = User(user_name="abc",user_phone="15927432501",application=app1)
#         self.assertIsNone(checkUserEnrolled(user2,app1))
    
#     def test_sign_response(self):
#         # account1,app1,user1,req,sig = getSig()
#         # auth_sig = signResponse(sig,app1.sKey)
#         auth_sig = 'AUTH|eHJifERhbFRFTjdBczlkSFcybExtVmNCfDE0ODcxNDgwNzQ=|b281615018801b7ac882361d4329f0da312e80da'
#         iKey = 'DalTEN7As9dHW2lLmVcB'
#         sKey = 'GkfLehUJ5Intoadm8m8yDtEZKHRDBH9ZrrUH5HmL'
#         print _parse_vals(sKey, auth_sig, 'AUTH', iKey)
#         print parseDuoSig(auth_sig)




        