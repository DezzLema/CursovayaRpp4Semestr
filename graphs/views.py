from django.shortcuts import render
from django.contrib import messages
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Graph, CustomUser, UserGallery
from .forms import GraphForm
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile
from .forms import AdminUserEditForm, AdminUserAddForm
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm, LoginForm


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


@login_required
def create_graph(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            graph = form.save(commit=False)
            graph.user = request.user
            graph.save()  # Автоматически сгенерирует изображение
            return redirect('gallery_list')
    else:
        form = GraphForm()
    return render(request, 'graphs/create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_graph(request, pk):
    graph = get_object_or_404(Graph, pk=pk)
    if request.method == 'POST':
        graph.delete()
        return redirect('gallery_list')
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
    graphs = Graph.objects.filter(user=user)
    return render(request, 'graphs/user_gallery.html', {
        'graphs': graphs,
        'gallery': gallery,
        'gallery_user': user
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
