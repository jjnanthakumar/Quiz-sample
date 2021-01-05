from django.shortcuts import render, redirect
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from .models import Quiz, Category
from django.views.decorators.csrf import csrf_exempt
import requests
import random
import json, time


def index(request):
    return render(request, 'index.html', {'title': 'Home Page'})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST) or None
        if form.is_valid():
            username = request.POST.get('username')
            d = {'username': username}
            form.save()
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    form = UserRegisterForm()
    return render(request, 'register.html', {'form': form, 'title': 'Registration'})


def Login(request):
    if request.method == 'POST':
        # request.session.set_test_cookie()
        username = request.POST.get('username')
        request.session['user'] = username
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)

            messages.success(request, f'welcome {username} !!')
            return redirect('index')
        else:
            messages.error(request, f'Invalid Username or Password :(')
    form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Sign In'})


questions = []


@csrf_exempt
def quiz(request):
    i = 0
    condition = {'gk': 9, 'cs': 18, 'maths': 19, 'sports': 21, 'music': 12, 'film': 11, 'books': 10}
    if request.method == 'GET':
        t1 = time.time()
        difficulty = request.GET.get('diff')
        print('***************')
        print(request.GET.get('category'))
        category = condition.get(request.GET.get('category'), 0)
        request.session['t1'] = t1
        request.session['cat_id'] = category
        request.session['cat_name'] = request.GET.get('category')
        request.session['diff'] = difficulty
        endpoint = 'https://opentdb.com/api.php?'
        data = requests.get(endpoint,
                            params={'amount': 10, 'type': 'multiple', 'difficulty': difficulty,
                                    'category': category}, verify=False).json()
        print(data)
        answers = data['results'][0]['incorrect_answers'] + [data['results'][0]['correct_answer']]
        random.shuffle(answers)
        request.session['questions'] = data['results'][1:]
        request.session['counter'] = i
        return render(request, 'quiz.html',
                      context={'question': data['results'][0]['question'],
                               'correct': data['results'][0]['correct_answer'], 'id': i + 1, 'answers': answers})


def question(request):
    if request.is_ajax():
        question, correct, answers = '', '', ''
        questions = request.session.get('questions')
        i = request.session.get('counter')
        request.session['score'] = request.GET.get('score')
        complete = False
        try:
            question = questions[i]['question']
            answers = questions[i]['incorrect_answers'] + [questions[i]['correct_answer']]
            random.shuffle(answers)
            correct = questions[i]['correct_answer']
            request.session['counter'] += 1
        except:
            t2 = time.time()
            timetaken = t2 - int(request.session.get('t1'))
            request.session['time'] = timetaken
            complete = True
        return HttpResponse(json.dumps({'question': question, 'id': i + 1, 'complete': complete,
                                        'correct': correct, 'answers': answers}),
                            content_type="application/json")


def result(request):
    diff_condition = {'easy': 0, 'medium': 1, 'hard': 2}
    score = int(request.session.get('score'))
    username = request.session.get('user')
    cat_id = request.session.get('cat_id')
    cat_name = request.session.get('cat_name')
    diff = request.session.get('diff')
    time = request.session.get('time')
    # categ = Category.objects.get(id=Category.objects.last().id, category_id=cat_id, category_name=cat_name,
    #                              user=User.objects.get(username=username),
    #                              category_diff=diff_condition.get(diff))
    # if not categ:
    category = Category()
    category.category_id = cat_id
    category.category_name = cat_name
    category.user = User.objects.get(username=username)
    category.score = score
    category.time_taken = time
    category.category_diff = diff_condition.get(diff)
    category.save()
    # else:
    #     categ.time_taken = time
    #     categ.score = score
    #     categ.save()
    quiz = Quiz()
    quiz.user = User.objects.get(username=username)
    quiz.save()
    for cat in Category.objects.filter(user=User.objects.get(username=username)):
        quiz.category.add(cat)
    messages.success(request, 'Results Saved Successfully :)')
    return render(request, 'result.html', {'final': score >= 5, 'timetaken': time, 'score': score})
