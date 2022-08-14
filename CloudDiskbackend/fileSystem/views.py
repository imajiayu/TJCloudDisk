import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from fileSystem.models import FileEntity,DirectoryEntity,FileDirectory
from django.utils import timezone
import CloudDisk.settings

# Create your views here.

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
class CsrfExemptSessionAuthentication(SessionAuthentication): 
    def enforce_csrf(self, request): 
        return  

class GetRootDir(APIView):
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
        dirs=DirectoryEntity.objects.filter(uid=user,parentid=rootdir)
        files=FileDirectory.objects.filter(did=rootdir)
        res = []
        for dir in dirs:
            res.append({ "type":"dir","id": dir.id, "name": dir.dname, "lastchange": dir.lastchange.strftime('%Y-%m-%d %H:%M:%S')})
        for file in files:
            res.append({"type":"file","id": file.id, "name": file.fname,"fsize":file.fid.fsize ,"lastchange": file.lastchange.strftime('%Y-%m-%d %H:%I:%S')})
        
        res.sort(key=lambda x:(x["type"],x['name']))
        return Response({
                "message":"success",
                "data":res,
                "rootid":rootdir.id
            })



class GetDir(APIView):
    def get(self, request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)

        pid=request.GET['pid']
        if not DirectoryEntity.objects.filter(uid=user,pk=int(pid)).exists():
            return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问"
                }
                },status=400)
        
        parentdir=DirectoryEntity.objects.get(pk=int(pid))
        dirs=DirectoryEntity.objects.filter(uid=user,parentid=parentdir)
        files=FileDirectory.objects.filter(did=parentdir)
        res = []

        for dir in dirs:
            res.append({ "type":"dir","id": dir.id, "name": dir.dname, "lastchange": dir.lastchange.strftime('%Y-%m-%d %H:%M:%S')})
        for file in files:
            res.append({"type":"file","id": file.id, "name": file.fname,"fsize":file.fid.fsize ,"lastchange": file.lastchange.strftime('%Y-%m-%d %H:%I:%S')})

        res.sort(key=lambda x:(x["type"],x['name']))
        return Response({
                "message":"success",
                "data":res
            })

class CreateDir(APIView):
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
            pid=request.data.get("pid")
            dname=request.data.get("dname")
            
            if not DirectoryEntity.objects.filter(pk=int(pid),uid=user).exists():#找不到父目录
                return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问"
                }
                },status=400)
            
            parentdir=DirectoryEntity.objects.get(pk=pid)
            if DirectoryEntity.objects.filter(uid=user,dname=dname,parentid=parentdir).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"当前目录下存在同名文件夹"
                }
                },status=400)
            else:
                DirectoryEntity.objects.create(dname=dname,uid=user,parentid=parentdir)
            updateLastChange(int(pid))
            return Response({
                "message":"success"
            })

def updateLastChange(pid):
    parentdir=DirectoryEntity.objects.get(pk=pid)
    while parentdir!=None:
        parentdir.lastchange=timezone.now()
        parentdir.save()
        parentdir=parentdir.parentid

class RenameDir(APIView):
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
            did=int(request.data.get("did"))
            dname=request.data.get("dname")
            
            if not DirectoryEntity.objects.filter(pk=int(did),uid=user).exists():#找不到目录
                return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问"
                }
                },status=400)

            dir=DirectoryEntity.objects.get(pk=did)
            if dname==dir.dname:
                return Response({
                "message":"success"
                })
            
            parentdir=DirectoryEntity.objects.get(pk=did).parentid
            if DirectoryEntity.objects.filter(uid=user,dname=dname,parentid=parentdir).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"当前目录下存在同名文件夹"
                }
                },status=400)

            DirectoryEntity.objects.filter(pk=did).update(dname=dname,lastchange=timezone.now())
            updateLastChange(dir.parentid.id)
            return Response({
                "message":"success"
                })

class RenameFile(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request):
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
            fname=request.data.get("fname")

            if not FileDirectory.objects.filter(pk=fid).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问"
                }
                },status=400)
            
            file=FileDirectory.objects.get(pk=fid)

            if file.fname==fname:
                return Response({
                    "message":"success"
                    })


            parentdir=file.did
            if FileDirectory.objects.filter(fname=fname,did=parentdir).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"当前目录下存在同名文件"
                }
                },status=400)
            
            file.fname=fname
            file.save()
            updateLastChange(parentdir.id)
            return Response({
                    "message":"success"
                    })

class RemoveDir(APIView):
    def get(self,request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            did=request.GET["did"]

            if not DirectoryEntity.objects.filter(uid=user,pk=int(did)).exists():
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"错误访问"
                    }
                    },status=400)
            removedir(did)

            dir=DirectoryEntity.objects.get(pk=int(did))
            updateLastChange(dir.parentid.id)
            dir.delete()
            return Response({
                    "message":"success"
                    })

class RemoveFile(APIView):
    def get(self,request):
        user=request.user
        if not user.is_authenticated:
            return Response({
                "message":"failure",
                "data":{
                    "detail":"用户未登录"
                }
                },status=400)
        else:
            fid=request.GET["fid"]

            if not FileDirectory.objects.filter(pk=int(fid)).exists():
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"错误访问"
                    }
                    },status=400)
            
            file=FileDirectory.objects.get(pk=int(fid))
            removefile(file.fid.id)
            file.delete()

            return Response({
                    "message":"success"
                    })

def removedir(did):
    files=getAllFiles(did)
    for file in files:
        removefile(file)

def removefile(fid):
    fileentity=FileEntity.objects.get(pk=fid)
    print(fileentity.link_num)
    if fileentity.link_num-1==0:
        os.system('rm -f '+os.path.join(CloudDisk.settings.FILE_POOL,fileentity.md5))
        fileentity.delete()
        return
    fileentity.link_num-=1
    fileentity.save()
    return


def getTree(pid):
    res = []
    parentdir=DirectoryEntity.objects.get(pk=pid)
    children=DirectoryEntity.objects.filter(parentid=parentdir)
    for child in children:
        t = {'label':child.dname,'isopen':False,'did':child.id}
        t['children']=getTree(child.id)
        res.append(t)
    
    return res

def getAllFiles(pid):
    res=[]
    parentdir=DirectoryEntity.objects.get(pk=pid)
    files=[x.fid.id for x in FileDirectory.objects.filter(did=parentdir)]
    res.extend(files)
    children=DirectoryEntity.objects.filter(parentid=parentdir)
    
    for child in children:
        res.extend(getAllFiles(child.id))

    return res
