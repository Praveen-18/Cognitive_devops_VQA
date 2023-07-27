from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Registration, Question
from django.contrib.auth.models import User
from .VQA_Image_Classifier.sample import answer_question, classify_image
import json
from VQA.svm_face_recognation.datasetCreation import VideoCamera, imageCapture
from django.http import StreamingHttpResponse
from VQA.svm_face_recognation.videocapture import Video , datacreation , lis , refresh
import pandas as pd
from fuzzywuzzy import fuzz

user_name = ""
def index(request):
    name = request.user.username.upper()
    return render(request, 'VQA/index.html', {'name': name})


def userlogin(request):
    if request.method == 'POST':
        print("Inside register")
        username = request.POST.get('username')
        password = request.POST.get('password')
        print("inside register : - ",username, password)
        curr_val = Registration(username=username, password=password)
        curr_val.save()
        user = User.objects.create_user(username=username, password=password)
        user.save()
        print(curr_val)
        if 'my_checkbox' in request.POST:
            # Checkbox is selected
            print("vsdg")
            user_name = username
            return render(request, 'VQA/imagecreation.html', {'name': username.upper()})
        return render(request, 'VQA/register.html')
    return render(request, 'VQA/login.html')


def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('userlogin')


def register(request):
    if request.user.is_authenticated:
        name = request.user.username.upper()
        return render(request, 'VQA/index.html', {'name': name})
    elif request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        curr_user = authenticate(username=username, password=password)
        print(username,password)
        if curr_user is not None:
            login(request, curr_user)
            if curr_user.is_superuser:
                return render(request, 'VQA/index.html', {'name': username.upper()})
            else:
                return redirect('index')  # Redirect to the desired page after successful login
        else:
            print("Invalid credentials")
            return render(request, 'VQA/register.html')
    else:
        return render(request, 'VQA/register.html')


def find_answer_explanation(input_classname):
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel('VQA/VQA_Image_Classifier/DATASET_VQA1.xls')

    # Calculate the fuzzy match score for each row in the 'classname' column
    df['fuzzy_score'] = df['class name'].apply(lambda x: fuzz.partial_ratio(input_classname, x))

    # Sort the DataFrame by fuzzy match score in descending order
    df = df.sort_values('fuzzy_score', ascending=False)

    # Get the row with the highest fuzzy match score (closest match)
    best_match = df.iloc[0]

    # Set the threshold for a minimum acceptable fuzzy match score (adjust as needed)
    min_acceptable_score = 70

    # Check if the best match has a score above the threshold
    if best_match['fuzzy_score'] >= min_acceptable_score:
        answer = best_match['answer']
        explanation = best_match['explanation']
        return answer, explanation
    else:
        return None, None

def vqa(request):
    if request.method == 'POST':
        questions = request.POST.get('questions')
        print(questions)
        image = request.FILES.get('image')
        if image:
            # Add image to the database
            my_model = Question(question=questions)
            my_model.image = image
            my_model.save()

            # Call the function from the other file
            image_path = my_model.image.path
            print(image_path)
            answer1 = classify_image(image_path, questions)
            print(answer1)
            input_classname = answer1
            answer, explanation = find_answer_explanation(input_classname)
            explanation = explanation.split(".")
            print(answer , explanation)

            if answer is not None and explanation is not None:
                print(f"Answer: {answer}")
                print(f"Explanation: {explanation}")
            else:
                print(f"No close match found for classname '{input_classname}'.")
            # print(questions)
            # print(answer)
            image_url = my_model.image.url if my_model.image else None
            if answer == "no":
                answer = "Apologies! 🙇‍♂️ Our cognitive devops team is still sharpening the AI's knowledge, and unfortunately, it hasn't learned about this specific input yet. Feel free to explore other questions or images, and we'll strive to improve the AI's capabilities for next time!"
            # print(answer)  # Print the answer for testing
            return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper(), 'answer': answer1,'question': questions,'image_url': image_url})

    return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper()})


def bmi_calculator(request):
    if request.method == 'POST':
        print("Inside BMI")
        feet = float(request.POST.get('feet'))
        weight = float(request.POST.get('weight'))
        height_in_cm = feet * 30.48
        bmi = calculate_bmi(height_in_cm, weight)
        category = get_bmi_category(bmi)
        print(height_in_cm, weight, bmi, category)
        result = {
            'height': round(height_in_cm, 2),
            'weight': weight,
            'bmi': bmi,
            'category': category
        }
        return HttpResponse(json.dumps(result), content_type='application/json')

    return render(request, 'VQA/BMI_Calculator.html', {'name': request.user.username.upper()})




def calculate_bmi(height, weight):
    # BMI Formula: BMI = weight (kg) / (height (m) * height (m))
    print(height, weight)
    height_in_meters = height / 100
    bmi = weight / (height_in_meters * height_in_meters)
    print(round(bmi, 2))
    return round(bmi, 1)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return 'UNDERWEIGHT'
    elif 18.5 <= bmi <= 24.9:
        return 'NORMAL WEIGHT'
    elif 25 <= bmi < 29.9:
        return 'OVERWEIGHT'
    else:
        return 'OBESE'

def blog(request):
    return render(request, 'VQA/blog.html', {'name': request.user.username.upper()})

def consultant(request):
    return render(request, 'VQA/consultant.html', {'name': request.user.username.upper()})

def blooddonation(request):
    return render(request, 'VQA/blooddonation.html', {'name': request.user.username.upper()})

def video_feed(request):
    return StreamingHttpResponse(imageCapture(VideoCamera() , "Praveen S" , 1), content_type='multipart/x-mixed-replace; boundary=frame')


def video_feed1(request):
    return StreamingHttpResponse(datacreation(Video() , request), content_type='multipart/x-mixed-replace; boundary=frame')

def stop_streaming1(request):
    if request.method == "POST":
        print("PRINTING")
        camera = Video()
        camera.stop_streaming()
        return render(request, 'vqa/imagecreation.html', {"status": True, "username": request.user , "lis" : []})
    l = list(lis())
    print(l)
    refresh()
    print(l)
    return render(request, 'vqa/index.html', {"status": False, "username": request.user , "lis" : l})


def stop_streaming(request):
    if request.method == "POST":
        print("PRINTING")
        # camera = VideoCamera()
        # camera.stop_streaming()
        return render(request, 'vqa/register.html', {"status": True, "username": request.user})
    return render(request, 'vqa/register.html', {"status": False, "username": request.user})

def uncapture(request):
    return render(request , 'vqa/register.html')

def uncapture1(request):
    val = lis()
    print(val)
    if max(val) == "Praveen S" or max(val) == "Praveen":
        return render(request , 'vqa/index.html' , {"name" : max(val)})
    else:
        return render(request , 'vqa/register.html')

def imagecreation(request):
    if request.method == "POST":
        return redirect('imagecreation')