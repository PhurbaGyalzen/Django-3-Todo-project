from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo_app/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo_app/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo_app/signupuser.html', {'form': UserCreationForm(), 'error': 'User already exists. Please try another username.'})

        else:
            return render(request, 'todo_app/signupuser.html', {'form': UserCreationForm(), 'error': 'Your password does not match.'})


def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo_app/loginuser.html', {'loginuser': AuthenticationForm()})
    else:
        user = authenticate(
            username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo_app/loginuser.html', {'loginuser': AuthenticationForm(), 'error': 'Username and Password does not match'})
        else:
            login(request, user)
            return redirect('currenttodos')


@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'todo_app/current.html', {'todos': todos})


@login_required
def createtodos(request):
    if request.method == "GET":
        return render(request, 'todo_app/createtodos.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo_app/createtodos.html', {'form': TodoForm(), 'error': 'Bad data inserted Please try again'})


@login_required
def viewtodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo_app/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo_app/viewtodo.html', {'todo': todo, 'form': form, 'error': 'Bad data inserted. please try again'})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == "POST":
        todo.delete()
        return redirect('currenttodos')


@login_required
def completetodos(request):
    if request.method == 'GET':
        todos = Todo.objects.filter(
            user=request.user,
            datecompleted__isnull=False,
        ).order_by('-datecompleted')
        return render(request, 'todo_app/completetodos.html', {'todos': todos})
