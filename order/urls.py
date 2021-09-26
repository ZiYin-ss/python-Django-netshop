# coding=utf-8

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ToOrderView.as_view()),
    url(r'^order.html$', views.OrderListView.as_view()),

]
