from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.accept, name='index'),
    url(r'^get_image/(?P<image_idx>[0-9]+)$', views.return_image, name='return_image'),
    url(r'^get_result/(?P<image_idx>[0-9]+.[0-9]+)$', views.return_test, name='return_extracted_image')
]