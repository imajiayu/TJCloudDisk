import os
from tempfile import tempdir
from django.http import FileResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from fileSystem.models import FileEntity,DirectoryEntity,FileDirectory
import CloudDisk.settings
from fileSystem.views import updateLastChange

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
class CsrfExemptSessionAuthentication(SessionAuthentication): 
    def enforce_csrf(self, request): 
        return  

class UploadFile1(APIView):
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
            md5=request.data.get("md5")
            pid=request.data.get("pid")
            fname=request.data.get("fname")

            if not DirectoryEntity.objects.filter(uid=user,pk=int(pid)).exists():
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"错误访问"
                    }
                    },status=400)

            parentdir=DirectoryEntity.objects.get(pk=pid)
            if FileEntity.objects.filter(md5=md5).exists():
                file=FileEntity.objects.filter(md5=md5)[0]
                file.link_num+=1
                file.save()
                fname1,fname2=os.path.splitext(fname)
                if FileDirectory.objects.filter(did=parentdir,fname=fname):
                    if FileDirectory.objects.filter(did=parentdir,fname=fname1+'-副本'+fname2):
                        i=1
                        fname=fname1+'-副本({0})'.format(i)+fname2
                        while FileDirectory.objects.filter(did=parentdir,fname=fname).exists():
                            i+=1
                            fname=fname1+'-副本({0})'.format(i)+fname2
                        FileDirectory.objects.create(fid=file,did=parentdir,fname=fname)
                    else:
                        FileDirectory.objects.create(fid=file,did=parentdir,fname=fname1+'-副本'+fname2)
                else:
                    FileDirectory.objects.create(fid=file,did=parentdir,fname=fname)
                updateLastChange(pid)
                return Response({
                    "message":"success"
                    })
            else:
                return Response({
                    "message":"failure"
                    },status=201)

class UploadFile2(APIView):
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
            md5=request.data.get("md5")
            files = request.FILES.getlist('file')

            if not DirectoryEntity.objects.filter(uid=user,pk=int(pid)).exists():
                return Response({
                    "message":"failure",
                    "data":{
                        "detail":"错误访问"
                    }
                    },status=400)

            file_path=None
            fname=None
            for f in files:
                file_path = os.path.join(CloudDisk.settings.FILE_POOL,md5)
                fname=f.name
                with open(file_path,'wb') as fp :
                    for chunk in f.chunks():
                        fp.write(chunk)

            fsize=os.path.getsize(file_path)
            file=FileEntity.objects.create(md5=md5,fsize=fsize,link_num=1)

            parentdir=DirectoryEntity.objects.get(pk=pid)
            files=FileDirectory.objects.filter(did=parentdir)


            fname1,fname2=os.path.splitext(fname)
            if FileDirectory.objects.filter(did=parentdir,fname=fname):
                if FileDirectory.objects.filter(did=parentdir,fname=fname1+'-副本'+fname2):
                    i=1
                    fname=fname1+'-副本({0})'.format(i)+fname2
                    while FileDirectory.objects.filter(did=parentdir,fname=fname).exists():
                        i+=1
                        fname=fname1+'-副本({0})'.format(i)+fname2
                    FileDirectory.objects.create(fid=file,did=parentdir,fname=fname)
                else:
                    FileDirectory.objects.create(fid=file,did=parentdir,fname=fname1+'-副本'+fname2)
            else:
                FileDirectory.objects.create(fid=file,did=parentdir,fname=fname)

            updateLastChange(pid)
            return Response({
                    "message":"success"
                    })

class UploadFile3(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    def post(self, request):
        return Response({
            "message":"success"
            })

class DownloadFile(APIView):
    def get(self, request):
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
            
            fid = request.GET.get('fid')

            if not FileDirectory.objects.filter(pk=fid).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"文件不存在",
                }
            },status=400)
            
            file=FileDirectory.objects.get(pk=fid)
            return FileResponse(open(os.path.join(CloudDisk.settings.FILE_POOL,file.fid.md5),'rb'),as_attachment=True,filename=file.fname)

class DownloadDir(APIView):
    def get(self, request):
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
            
            did = request.GET.get('did')

            if not DirectoryEntity.objects.filter(pk=did,uid=user).exists():
                return Response({
                "message":"failure",
                "data":{
                    "detail":"错误访问",
                }
            },status=400)

            dir=DirectoryEntity.objects.get(pk=did)
            
            createDir([],did)

            file_path=os.path.join(CloudDisk.settings.TEMP_DIR,dir.dname)
            command="tar -zcvf "+dir.dname+'.tar.gz '+dir.dname
            os.system("cd /home/mjy/CloudDisk/tempdir;"+command)
            ret = FileResponse(open(os.path.join(CloudDisk.settings.TEMP_DIR,dir.dname+'.tar.gz'),'rb'),as_attachment=True,filename=dir.dname+'.tar.gz')
            os.system("rm -rf "+file_path)
            os.system("rm -f "+os.path.join(CloudDisk.settings.TEMP_DIR,dir.dname+'.tar.gz'))
            return ret

def createDir(path,did):
    dir=DirectoryEntity.objects.get(pk=did)
    path.append(dir.dname)
    realpath="/".join(path)
    command="mkdir "+os.path.join(CloudDisk.settings.TEMP_DIR,realpath)
    os.system(command)

    files=FileDirectory.objects.filter(did=dir)
    for file in files:
        command="cp "+os.path.join(CloudDisk.settings.FILE_POOL,file.fid.md5)+' '+os.path.join(CloudDisk.settings.TEMP_DIR,realpath,file.fname)
        print(command)
        os.system(command)

    children = DirectoryEntity.objects.filter(parentid=dir)
    for child in children:
        createDir(path,child.id)
    path.pop()