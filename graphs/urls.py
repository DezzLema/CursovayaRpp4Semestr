from django.urls import path
from . import views

urlpatterns = [
    path('', views.graph_list, name='graph_list'),
    path('create/', views.create_graph, name='create_graph'),
    path('delete/<int:pk>/', views.delete_graph, name='delete_graph'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # URL-адреса админ-панели
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/users/', views.user_list, name='user_list'),
    path('admin-panel/users/<int:pk>/', views.user_detail, name='user_detail'),
    path('admin-panel/users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('admin-panel/users/<int:pk>/delete/', views.delete_user, name='delete_user'),
    path('admin-panel/users/add/', views.add_user, name='add_user'),
]
