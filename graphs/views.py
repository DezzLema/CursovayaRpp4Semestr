from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Graph, CustomUser
from .forms import GraphForm
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from django.core.files.base import ContentFile

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
    graphs = Graph.objects.all()
    return render(request, 'graphs/list.html', {'graphs': graphs})


@login_required
def create_graph(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            graph = form.save(commit=False)
            graph.user = request.user
            graph.save()  # Автоматически сгенерирует изображение
            return redirect('graph_list')
    else:
        form = GraphForm()
    return render(request, 'graphs/create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_graph(request, pk):
    graph = get_object_or_404(Graph, pk=pk)
    if request.method == 'POST':
        graph.delete()
        return redirect('graph_list')
    return render(request, 'graphs/delete.html', {'graph': graph})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Автоматически сохранит с user_type='registered'
            login(request, user)
            return redirect('graph_list')
    else:
        form = RegisterForm()
    return render(request, 'graphs/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('graph_list')
    else:
        form = LoginForm()
    return render(request, 'graphs/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('graph_list')
