from turtle import mode
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FileEntity(models.Model):
    md5 = models.CharField(max_length=128)
    fsize = models.IntegerField()
    link_num = models.IntegerField()
    

class DirectoryEntity(models.Model):
    dname = models.CharField(max_length=128)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    parentid= models.ForeignKey('self',on_delete=models.CASCADE,null=True)
    lastchange = models.DateTimeField(default=timezone.now)

class FileDirectory(models.Model):
    lastchange = models.DateTimeField(default=timezone.now)
    fid=models.ForeignKey(FileEntity,on_delete=models.CASCADE)
    did=models.ForeignKey(DirectoryEntity,on_delete=models.CASCADE)
    fname=models.CharField(max_length=128)
    class Meta:
        unique_together = ("fid", "did","fname")
        