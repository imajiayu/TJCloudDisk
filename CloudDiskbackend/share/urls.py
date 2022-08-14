from django.urls import path
from . import views

urlpatterns = [
    path("getdirtree/",views.GetDirTree.as_view(), name='getdirtree'),
    path("movefile/",views.MoveFile.as_view(), name='movefile'),
    path("copyfile/",views.CopyFile.as_view(), name='copyfile'),
    path("copydir/",views.CopyDir.as_view(), name='copydir'),
    path("movedir/",views.MoveDir.as_view(),name="movedir"),
    path("getsharetoken/",views.GetShareToken.as_view(),name="getsharetoken"),
    path("verifysharetoken/",views.VerifyShareToken.as_view(),name="verifysharetoken")
]