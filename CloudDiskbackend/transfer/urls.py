from django.urls import path
from . import views

urlpatterns = [
    path("uploadfile1/",views.UploadFile1.as_view(), name='uploadfile1'),
    path("uploadfile2/",views.UploadFile2.as_view(), name='uploadfile2'),
    path("uploadfile3/",views.UploadFile3.as_view(), name='uploadfile3'),
    path("downloadfile/",views.DownloadFile.as_view(), name='downloadfile'),
    path("downloaddir/",views.DownloadDir.as_view(), name='downloaddir'),
]
