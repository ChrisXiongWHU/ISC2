#coding:utf-8

from django.shortcuts import render,get_object_or_404,redirect
from .models import Application,Account,User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest,HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from .duoTools import parseDuoSig,validateParams,checkUserEnrolled,signResponse,DuoFormatException,getIp
from django.db.utils import IntegrityError

from django.urls import reverse
import requests
from duo import _parse_vals
import logging
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

    # print 'In auth_pre iKey: %s' %(iKey)
    # print 'In auth_pre iKey type is %s' %(str(type(iKey)))
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
    # request.session['iKey'] = iKey
    # print 'In session iKey : %s' %(request.session['iKey'])
    # print 'In session sig_dict iKey : %s' %(request.session['sig_dict']['content'][1])

    if user is not None:
        authUrl = reverse('duos:auth',args=(api_hostname,))
        #获取远方用户IP
        ip = getIp(request)
        request.session['ip'] = ip
        return redirect(authUrl)
    else:
        enrollUrl = reverse('duos:enroll',args=(api_hostname,))
        return redirect(enrollUrl)

@xframe_options_exempt
def auth(request,api_hostname):
    if request.method == 'GET':
        return render(request,'duos/auth.html',{'api_hostname':api_hostname})
    elif request.method == 'POST':
        sigDict = request.session.get('sig_dict',None)
        parent = request.session.get('parent',None)
        sKey = request.session.get('sKey',None)
        ip = request.session.get('ip',None)
        # iKey = request.session.get('iKey',None)

        # print 'in Auth iKey : %s' %(iKey)
        responseBody = signResponse(sigDict,sKey)
        # print 'in auth:sigDict iKey : %s' %(sigDict['content'][1])
        # requests.post(parent,data={'sig_response':responseBody,
        # 'sKey':sKey,
        # 'iKey':iKey})

        #删除session
        del request.session['sig_dict']
        del request.session['parent']
        del request.session['sKey']
        del request.session['ip']

        print parent
        print ip
        # print 'post back %s ' %(responseBody)
        return render(request,'duos/auth_succeed.html',{
            'parent':parent,
            'data':responseBody
        })




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
        return redirect(reverse('duos:auth',args=(api_hostname,)))


        



    
        
    


    
    
    
    
