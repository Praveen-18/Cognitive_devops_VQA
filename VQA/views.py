from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Registration, Question
from django.contrib.auth.models import User
from .VQA_Image_Classifier.sample import answer_question, classify_image


def index(request):
    name = request.user.username.upper()
    return render(request, 'VQA/index.html', {'name': name})


def userlogin(request):
    if request.user.is_authenticated:
        name = request.user.username.upper()
        return render(request, 'VQA/index.html', {'name': name})
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        curr_user = authenticate(username=username, password=password)
        if curr_user is not None:
            login(request, curr_user)
            if curr_user.is_superuser:
                return render(request, 'VQA/index.html', {'name': username.upper()})
            else:
                return redirect('index')  # Redirect to the desired page after successful login
        else:
            return render(request, 'VQA/login.html')
    else:
        return render(request, 'VQA/login.html')


def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('userlogin')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        curr_val = Registration(username=username, password=password)
        curr_val.save()
        user = User.objects.create_user(username=username, password=password)
        user.save()
        print(curr_val)
        return render(request, 'VQA/register.html')
    else:
        return render(request, 'VQA/register.html')


def vqa(request):
    if request.method == 'POST':
        questions = request.POST.get('questions')
        image = request.FILES.get('image')
        if image:
            # Add image to the database
            my_model = Question(question=questions)
            my_model.image = image
            my_model.save()

            # Call the function from the other file
            answer = answer_question(my_model.image.name, questions)
            print(answer)  # Print the answer for testing
            return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper(), 'answer': answer})

    return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper()})