from django.urls import path
from . import views

urlpatterns = [
    path("getroot/",views.GetRootDir.as_view(), name='getroot'),
    path("getdir/",views.GetDir.as_view(), name='getdir'),
    path("createdir/",views.CreateDir.as_view(), name='createdir'),
    path("renamedir/",views.RenameDir.as_view(), name='renamedir'),
    path("renamefile/",views.RenameFile.as_view(), name='renamefile'),
    path("removedir/",views.RemoveDir.as_view(),name="removedir"),
    path("removefile/",views.RemoveFile.as_view(),name="removefile"),
]

# {
# "username":"mjy",
# "password":"123456",
# "email":""
# }