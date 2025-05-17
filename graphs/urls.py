from django.urls import path
from . import views

urlpatterns = [
    path('', views.graph_list, name='graph_list'),
    path('create/', views.create_graph, name='create_graph'),
    path('delete/<int:pk>/', views.delete_graph, name='delete_graph'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]