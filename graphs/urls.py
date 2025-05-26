from django.urls import path
from . import views
from .views import gallery_list

urlpatterns = [

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

    # галерея
    path('', views.gallery_list, name='gallery_list'),  # Главная страница с галереями
    path('graphs/', views.graph_list, name='graph_list'),  # Старый маршрут для списка графиков (если нужен)
    path('gallery/<int:user_id>/', views.user_gallery, name='user_gallery'),
    path('create/', views.create_graph, name='create_graph'),

    path('', views.gallery_list, name='gallery_list'),
    path('gallery/<int:user_id>/', views.user_gallery, name='user_gallery'),
    path('graph/create/', views.create_graph, name='create_graph'),
    path('graph/delete/<int:pk>/', views.delete_graph, name='delete_graph'),
    path('graph/<int:graph_id>/image/', views.generate_graph, name='generate_graph'),
    path('gallery/edit/', views.edit_gallery, name='edit_gallery'),
    path('gallery/edit/', views.edit_gallery, name='edit_gallery'),  # Для своей галереи
    path('gallery/<int:user_id>/edit/', views.edit_gallery, name='edit_user_gallery'),  # Для чужой галереи (админ)
    path('graph/create/', views.create_graph, name='create_graph'),  # Для своей галереи
    path('graph/<int:user_id>/create/', views.create_graph, name='create_user_graph'),  # Для чужой галереи (админ)
]
