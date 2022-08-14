from django.urls import path
from . import views

urlpatterns = [
    path("verify/",views.Verify.as_view(), name='verify'),
    path("register/",views.Register.as_view(), name='register'),
    path("myinfo/", views.MyInfo.as_view(), name="myinfo"),
    path('login/', views.Login.as_view(), name='login'),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("getIdentity/", views.GetIdentity.as_view(), name="getIdentity"),
    path('forgetpassword1/', views.ForgetPasswd1.as_view(), name='forgetpassword1'),
    path('forgetpassword2/', views.ForgetPasswd2.as_view(), name='forgetpassword2'),
    path("uploadavatar/", views.UploadAvatar.as_view(), name="uploadavatar"),
]