#coding:utf-8

from django.shortcuts import render,get_object_or_404,redirect
from .models import Application,Account,User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest,HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .duoTools import parseDuoSig,validateParams,checkUserEnrolled,signResponse,DuoFormatException
from django.db.utils import IntegrityError

from django.urls import reverse
from channels import Group
from channels.asgi import get_channel_layer
from django.core.cache import cache
import requests
from duo import _parse_vals
import json
import time
# Create your views here.



@xframe_options_exempt
def auth_pre(request,api_hostname):
    '''
    接受request，request data为tx,parent
    对tx进行验证，未通过则返回错误
    检测user是否enroll，若未enroll进行enroll操作，否则进行验证操作
    '''


    try:
        app = Application.objects.get(api_hostname = api_hostname)
    except Application.DoesNotExist,e:
         return render(request,'duos/not_found.html')

    iKey = app.iKey
    sKey = app.sKey
    tx = request.GET['tx']
    parent = request.GET['parent']
    #若sig存在格式错误，返回403
    try:
        sig = parseDuoSig(tx)
    except DuoFormatException,e:
        return render(request,'duos/dennied.html')

    #若sig存在信息错误，iKey不匹配或加密错误，返回403
    if not validateParams(sig,iKey,sKey):
        return render(request,'duos/dennied.html')

    #若user未enroll，进行enroll否则进行认证
    userName = sig['content'][0]
    user = checkUserEnrolled(userName,app)

    #保存sig_dict，parent,sKey供enroll和认证使用
    request.session['sig_dict'] = sig
    request.session['parent'] = parent
    request.session['sKey'] = sKey

    if user is not None:
        return render(request,'duos/auth.html',{
            'api_hostname':api_hostname
        })
    else:
        enrollUrl = reverse('duos:enroll',args=(api_hostname,))
        return redirect(enrollUrl)

@xframe_options_exempt
def auth_check_ws(request,api_hostname):
    account = Account.objects.get(application__api_hostname=api_hostname)
    phone = account.account_phone
    channel_layer = get_channel_layer()
    request.session['phone'] = phone

    # 每5秒检查一次socket连接,最多不超过30秒
    for i in xrange(6):
        print 'check socket linking %d' %i
        mobile_group_list = channel_layer.group_channels("phone-%s" %phone)
        if len(mobile_group_list)>0:
            Group("phone-%s" %phone).send({"text":"auth"})
            return HttpResponse(content=json.dumps({'status':'ok'}))
        else:
            time.sleep(5)
    # 30秒内未发现可用连接
    else:
        return HttpResponse(content=json.dumps({'status':'pending'}))
    


def auth(request,api_hostname):
    phone = request.session['phone']
    del request.session['phone']
    mobile_group_list = get_channel_layer().group_channels("phone-%s" %phone)
    time.sleep(5)
    #若连接中断
    if len(mobile_group_list) == 0:
        return HttpResponse(content=json.dumps({'status':'pending'}))

    # 每5秒检查一次认证情况,最多不超过30秒
    for i in xrange(6):
        auth_status = cache.get('%s_auth_status'% phone,None)
        # 认证成功
        if auth_status is True:
            sigDict = request.session.get('sig_dict',None)
            parent = request.session.get('parent',None)
            sKey = request.session.get('sKey',None)
            responseBody = signResponse(sigDict,sKey)
            return HttpResponse(content=json.dumps({
                'status':'ok',
                'data':responseBody,
                'parent':parent
            }))
        # 认证失败
        elif auth_status is False:
            return HttpResponse(content=json.dumps({'status':'failed'}))
        else:
            time.sleep(5)
    # 认证未进行
    else:
        return HttpResponse(content=json.dumps({'status':'pending'}))




            
                
                
    # if request.method == 'GET':
    #     return render(request,'duos/auth.html',{'api_hostname':api_hostname})
    # elif request.method == 'POST':
    #     sigDict = request.session.get('sig_dict',None)
    #     parent = request.session.get('parent',None)
    #     sKey = request.session.get('sKey',None)
    #     ip = request.session.get('ip',None)
    
    #     responseBody = signResponse(sigDict,sKey)
     
    #     #删除session
    #     del request.session['sig_dict']
    #     del request.session['parent']
    #     del request.session['sKey']
    
    #     return render(request,'duos/auth_succeed.html',{
    #         'parent':parent,
    #         'data':responseBody
    #     })




@xframe_options_exempt
def enroll(request,api_hostname):
    #如果该请求为auth_pre发送
    if request.method == 'GET':
        return render(request,'duos/enroll.html', \
        {'api_hostname':api_hostname})

    #若该请求为提交表单
    elif request.method =='POST':
        phone = request.POST['phone']
        userName = request.session.get('sig_dict',None)['content'][0]
        parent = request.session.get('parent',None)
        app = Application.objects.get(api_hostname = api_hostname)

        #防止重复提交表单，捕获实体完整性错误
        try:
             user = User.objects.create(user_name=userName,user_phone=phone,application=app)
        except IntegrityError,e:
            pass
        return render(request,'duos/auth.html',{
            'api_hostname':api_hostname
        })


        



    
        
    


    
    
    
    
