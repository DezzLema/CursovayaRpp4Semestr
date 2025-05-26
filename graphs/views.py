from django.shortcuts import render
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Graph, CustomUser, UserGallery
from .forms import GraphForm, GalleryEditForm
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile
from .forms import AdminUserEditForm, AdminUserAddForm
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm
from django.http import HttpResponse


def is_admin(user):
    return user.user_type == 'admin'


def is_registered(user):
    return user.user_type == 'registered'


def generate_parabola(a, b, c):
    x = np.linspace(-10, 10, 400)
    y = a * x ** 2 + b * x + c

    plt.figure()
    plt.plot(x, y)
    plt.title(f'График функции: y = {a}x² + {b}x + {c}')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.grid(True)

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()

    return buffer.getvalue()


def graph_list(request):
    return redirect('gallery_list')


class PermissionDenied:
    pass


@login_required
def create_graph(request, user_id=None):
    if not request.user.is_authenticated or request.user.user_type not in ['admin', 'registered']:
        raise PermissionDenied("У вас нет прав для создания графиков")

    # Определяем целевого пользователя
    target_user = get_object_or_404(CustomUser, pk=user_id) if user_id else request.user

    # Проверка прав: либо это владелец, либо админ
    if not (request.user == target_user or request.user.user_type == 'admin'):
        raise PermissionDenied("У вас нет прав для создания графиков в этой галерее")

    if request.method == 'POST':
        form = GraphForm(request.POST, user=request.user, target_user=target_user)
        if form.is_valid():
            graph = form.save()
            messages.success(request, 'График успешно добавлен в галерею')
            return redirect('user_gallery', user_id=target_user.id)
    else:
        form = GraphForm(user=request.user, target_user=target_user)

    return render(request, 'graphs/create.html', {
        'form': form,
        'is_owner': request.user == target_user,
        'target_user': target_user
    })


@login_required
def delete_graph(request, pk):
    graph = get_object_or_404(Graph, pk=pk)

    # Проверка прав
    is_owner = request.user == graph.user
    is_admin = request.user.user_type == 'admin'

    if not (is_owner or is_admin):
        raise PermissionDenied("У вас нет прав для удаления этого графика")

    if request.method == 'POST':
        graph.delete()
        messages.success(request, 'График успешно удален')
        return redirect('user_gallery', user_id=request.user.id)

    return render(request, 'graphs/delete.html', {'graph': graph})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сигнал автоматически создаст галерею
            login(request, user)
            return redirect('gallery_list')
    else:
        form = RegisterForm()
    return render(request, 'graphs/register.html', {'form': form})


def gallery_list(request):
    galleries = UserGallery.objects.all().select_related('user')
    return render(request, 'graphs/list.html', {'galleries': galleries})


def user_gallery(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    gallery = get_object_or_404(UserGallery, user=user)

    # Проверка прав доступа
    is_owner = request.user == user
    is_admin = request.user.is_authenticated and request.user.user_type == 'admin'

    if request.method == 'POST' and (is_owner or is_admin):
        # Логика добавления графиков (если нужно)
        pass

    graphs = gallery.graphs.all()  # Теперь используем related_name

    return render(request, 'graphs/user_gallery.html', {
        'graphs': graphs,
        'gallery': gallery,
        'gallery_user': user,
        'is_owner': is_owner,
        'is_admin': is_admin
    })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('gallery_list')
    else:
        form = LoginForm()
    return render(request, 'graphs/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('gallery_list')


@login_required
@user_passes_test(is_admin)
def admin_panel(request):
    return render(request, 'graphs/admin_panel.html')


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'graphs/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'graphs/user_detail.html', {'user': user})


@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Пользователь успешно обновлен')
            return redirect('user_detail', pk=user.pk)
    else:
        form = AdminUserEditForm(instance=user)
    return render(request, 'graphs/edit_user.html', {'form': form, 'user': user})


@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Пользователь успешно удален')
        return redirect('user_list')
    return render(request, 'graphs/delete_user.html', {'user': user})


@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = AdminUserAddForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сигнал автоматически создаст галерею
            messages.success(request, 'Пользователь успешно создан')
            return redirect('user_detail', pk=user.pk)
    else:
        form = AdminUserAddForm()
    return render(request, 'graphs/add_user.html', {'form': form})


def generate_graph(request, graph_id):
    graph = get_object_or_404(Graph, pk=graph_id)
    image_data = graph.generate_graph_image()

    response = HttpResponse(image_data, content_type='image/png')
    response['Cache-Control'] = 'max-age=3600'  # Кэшируем на 1 час
    return response


@login_required
def edit_gallery(request, user_id=None):
    # Если user_id не указан (обычный пользователь) или если это админ редактирует чужую галерею
    target_user = get_object_or_404(CustomUser, pk=user_id) if user_id else request.user

    # Проверка прав: либо это владелец, либо админ
    if not (request.user == target_user or request.user.user_type == 'admin'):
        raise PermissionDenied("У вас нет прав для редактирования этой галереи")

    gallery = get_object_or_404(UserGallery, user=target_user)

    if request.method == 'POST':
        form = GalleryEditForm(request.POST, instance=gallery, target_user=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Галерея успешно изменена')
            return redirect('user_gallery', user_id=target_user.id)
    else:
        form = GalleryEditForm(instance=gallery, target_user=target_user)

    return render(request, 'graphs/edit_gallery.html', {
        'form': form,
        'gallery': gallery,
        'target_user': target_user
    })