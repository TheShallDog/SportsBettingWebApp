from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name="index"),
    path('update_page/', views.update_page, name="update_page"),
    path('reset_test_tables/', views.reset_test_tables, name="reset_test_tables"),
    path('my_view/', views.my_view, name="my_view"),
]
