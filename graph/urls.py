from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
     url(r'api/(?P<place>.*)$',views.api,name='js_api'),
     url('^$', views.index, name='index_base'),
     url('^aklhakjfhljhxliuyasfxjh', views.index_m, name='index_base_m'),

]

