from django.contrib import admin
from fileSystem.models import FileEntity,FileDirectory,DirectoryEntity
# Register your models here.
admin.site.register([FileEntity,FileDirectory,DirectoryEntity])