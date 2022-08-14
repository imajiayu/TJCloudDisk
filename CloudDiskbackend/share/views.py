import os
import random
from rest_framework.views import APIView
from rest_framework.response import Response
from fileSystem.models import FileEntity,DirectoryEntity,FileDirectory
from fileSystem.views import getTree, removefile, updateLastChange
from django.utils import timezone
import CloudDisk.settings
import redis

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
class CsrfExemptSessionAuthentication(SessionAuthentication): 
    def enforce_csrf(self, request): 
        return  

# Create your views here.
class MoveFile(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request):
        # 判断用户登录
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            fid=int(request.data.get("fid"))
            pid=int(request.data.get("pid"))

            file=FileDirectory.objects.get(pk=fid)
            parentdir=DirectoryEntity.objects.get(pk=pid)

            if parentdir.id==file.did.id:
                return Response({
                "message":"success"
                })

            fname=file.fname
            fname1,fname2=os.path.splitext(fname)
            if FileDirectory.objects.filter(did=parentdir,fname=fname):
                if FileDirectory.objects.filter(did=parentdir,fname=fname1+'-副本'+fname2):
                    i=1
                    fname=fname1+'-副本({0})'.format(i)+fname2
                    while FileDirectory.objects.filter(did=parentdir,fname=fname).exists():
                        i+=1
                        fname=fname1+'-副本({0})'.format(i)+fname2
                    FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname)
                else:
                    FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname1+'-副本'+fname2)
            else:
                FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname)

            updateLastChange(file.did.id)
            updateLastChange(pid)
            file.delete()

            return Response({
                "message":"success"
                })

class CopyFile(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self,request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            fid=int(request.data.get("fid"))
            pid=int(request.data.get("pid"))

            file=FileDirectory.objects.get(pk=fid)
            parentdir=DirectoryEntity.objects.get(pk=pid)

            fname=file.fname
            fname1,fname2=os.path.splitext(fname)
            if FileDirectory.objects.filter(did=parentdir,fname=fname):
                if FileDirectory.objects.filter(did=parentdir,fname=fname1+'-副本'+fname2):
                    i=1
                    fname=fname1+'-副本({0})'.format(i)+fname2
                    while FileDirectory.objects.filter(did=parentdir,fname=fname).exists():
                        i+=1
                        fname=fname1+'-副本({0})'.format(i)+fname2
                    FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname)
                else:
                    FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname1+'-副本'+fname2)
            else:
                FileDirectory.objects.create(fid=file.fid,did=parentdir,fname=fname)

            file.fid.link_num+=1
            file.fid.save()
            updateLastChange(pid)

            return Response({
                "message":"success"
                })

class MoveDir(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self,request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            did=int(request.data.get("did"))
            pid=int(request.data.get("pid"))

            parentdir=DirectoryEntity.objects.get(pk=pid)
            dir=DirectoryEntity.objects.get(pk=did)

            if dir.parentid.id==pid:
                return Response({
                    "message":"success"
                    })
            
            temp=parentdir
            while temp:
                if temp.id==did:
                    return Response({
                    "message":"failure",
                    "data":{
                        "detail":"无法将文件移动至其自身下"
                    }
                    },status=400)
                temp=temp.parentid

            dname=dir.dname
            newdir=None

            if DirectoryEntity.objects.filter(parentid=parentdir,dname=dname):
                if DirectoryEntity.objects.filter(parentid=parentdir,dname=dname+'-副本'):
                    i=1
                    dname=dname+'-副本({0})'.format(i)
                    while DirectoryEntity.objects.filter(parentid=parentdir,dname=dname).exists():
                        i+=1
                        dname=dir.dname+'-副本({0})'.format(i)
                    newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname)
                else:
                    newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname+'-副本')
            else:
                newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname)

            copydir(user,newdir.id,did)
            updateLastChange(pid)


            
            updateLastChange(dir.parentid.id)
            dir.delete()

            return Response({
            "message":"success"
            })

class CopyDir(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self,request):
        
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            did=int(request.data.get("did"))
            pid=int(request.data.get("pid"))

            parentdir=DirectoryEntity.objects.get(pk=pid)
            dir=DirectoryEntity.objects.get(pk=did)

            temp=parentdir
            while temp:
                if temp.id==did:
                    return Response({
                    "message":"failure",
                    "data":{
                        "detail":"无法将文件移动至其自身及子目录下"
                    }
                    },status=400)
                temp=temp.parentid


            dname=dir.dname

            newdir=None

            if DirectoryEntity.objects.filter(parentid=parentdir,dname=dname):
                if DirectoryEntity.objects.filter(parentid=parentdir,dname=dname+'-副本'):
                    i=1
                    dname=dname+'-副本({0})'.format(i)
                    while DirectoryEntity.objects.filter(parentid=parentdir,dname=dname).exists():
                        i+=1
                        dname=dir.dname+'-副本({0})'.format(i)
                    newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname)
                else:
                    newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname+'-副本')
            else:
                newdir=DirectoryEntity.objects.create(uid=user,parentid=parentdir,dname=dname)

            copydir(user,newdir.id,did)
            updateLastChange(pid)

            return Response({
            "message":"success"
            })
            
def copydir(user,newid,oldid):
    olddir=DirectoryEntity.objects.get(pk=oldid)
    newdir=DirectoryEntity.objects.get(pk=newid)

    files=FileDirectory.objects.filter(did=olddir)
    for file in files:
        FileDirectory.objects.create(fid=file.fid,did=newdir,fname=file.fname)
        file.fid.link_num+=1
        file.fid.save()
    
    dirs=DirectoryEntity.objects.filter(parentid=olddir)
    for dir in dirs:
        t=DirectoryEntity.objects.create(uid=user,dname=dir.dname,parentid=newdir)
        copydir(user,t.id,dir.id)



class GetDirTree(APIView):
    def get(self, request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        
        rootdir=DirectoryEntity.objects.get(uid=user,dname="root",parentid=None)
        return Response({
            "message":"success",
            "data": [{'label':'root','isopen':True,'children':getTree(rootdir.id),'did':rootdir.id}]
            })

class GetShareToken(APIView):
    def get(self, request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)

        type=request.GET['type']
        id=int(request.GET['id'])

        if type=="file" and not FileDirectory.objects.filter(pk=id).exists \
             or type=="dir" and not DirectoryEntity.objects.filter(pk=id).exists:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问"
                }
                },status=400)
        
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
        characters = "".join(random.sample(alphabet, 32))

        

        r = redis.Redis(host='localhost', port=6379, db=0)

        r.hset(characters,"type",type)
        r.hset(characters,"id",id)
        r.expire(characters,3600)

        return Response({
            "message":"success",
            "token": characters
            })


class VerifyShareToken(APIView):
    def get(self, request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        
        else:

            token=request.GET['token']

            r = redis.Redis(host='localhost', port=6379, db=0)
            if not r.exists(token):
                return Response ({
                "message":"failure",
                "data":{
                    "detail":"分享链接不存在或已失效"
                }
                },status=400)
            else:
                type=r.hget(token,"type").decode()
                id=int(r.hget(token,"id"))

                if type=="dir" and not DirectoryEntity.objects.filter(pk=id).exists() or\
                    type=="file" and not FileDirectory.objects.filter(pk=id).exists():
                    return Response({
                    "message":"failure",
                    "data":{
                        "detail":"文件已不存在"
                    }
                    },status=401)

                if type=="file":
                    file=FileDirectory.objects.get(pk=id)
                    return Response({
                        "message":"success",
                        "data":[{"type":type,"id":id,"name":file.fname,"fsize":file.fid.fsize,"lastchange":file.lastchange.strftime('%Y-%m-%d %H:%M:%S')}]
                    })
                else:
                    dir=DirectoryEntity.objects.get(pk=id)
                    return Response({
                        "message":"success",
                        "data":[{"type":type,"id":id,"name":dir.dname,"lastchange":dir.lastchange.strftime('%Y-%m-%d %H:%M:%S')}] 
                    })