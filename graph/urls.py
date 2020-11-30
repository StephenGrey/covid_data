from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
     url('^aklhakjfhljhxliuyasfxjh/place=(?P<place>.*)$', views.index_m, name='index_base_m_o'),
     url('^aklhakjfhljhxliuyasfxjh', views.index_m, name='index_base_m'),
     url('^aklhlkjlkfzkerxsfxjh', views.sparks, name='sparks'),
     url('^ons_api/(?P<place>.*)$', views.fetch_ons, name='fetch_ons'),
     url('^api_rates$',views.api_rates,name='js_api_rates'),
     url('^api_shapes$',views.api_shapes,name='js_api_shapes'),
     url('^api/(?P<place>.*)$',views.api,name='js_api'),
     url('^place=(?P<place>.*)$',views.index,name='index_base_o'),
     url('^$', views.index, name='index_base'),

]

