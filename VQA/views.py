from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from .models import Registration, Question, BloodDonation, Doctor_register, Consultant, Appointment_status, Blog, Feedback, User_Wallet
from django.contrib.auth.models import User
from .VQA_Image_Classifier.sample import answer_question, classify_image
import json
from VQA.svm_face_recognation.datasetCreation import VideoCamera, imageCapture
from django.http import StreamingHttpResponse
from VQA.svm_face_recognation.videocapture import Video , datacreation , lis , refresh
import pandas as pd
from fuzzywuzzy import fuzz
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST

user_name = ""
def index(request):
    name = request.user.username.upper()
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0
    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False
    return render(request, 'VQA/index.html', {'name': name, 'status': status,'amt':amt})


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
    return redirect('register')


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



def separate_text_by_dot(text):
    # Split the text into individual sentences based on the dot (".") as a delimiter
    sentences = text.split(". ")

    # Remove any leading or trailing whitespaces from each sentence
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    return sentences

def vqa(request):
    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0
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
            print(answer, explanation)

            explain_str = []  # Initialize with an empty list

            if answer is not None and explanation is not None:
                print(f"Answer: {answer}")

                if explanation.strip():
                    sentences = separate_text_by_dot(explanation)
                    explanation_str = '. '.join(sentences)

                    if explanation_str.endswith('. '):
                        explanation_str = explanation_str[:-2]

                    explain_str = explanation_str.split(". ")

                    for sentence in explain_str:
                        print(sentence)

                else:
                    explanation_str = "No explanation available."
                    print(explanation_str)

            else:
                print(f"No close match found for classname '{input_classname}'.")
                explanation_str = "No explanation available."
                explain_str = "No explanation available."
                print(explanation_str)


            image_url = my_model.image.url if my_model.image else None
            if answer == "no":
                answer = "Apologies! 🙇‍♂️ Our cognitive devops team is still sharpening the AI's knowledge, and unfortunately, it hasn't learned about this specific input yet. Feel free to explore other questions or images, and we'll strive to improve the AI's capabilities for next time!"

            return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper(), 'answer': answer1, 'question': questions, 'image_url': image_url, 'explanation': explain_str, 'answer1': answer, 'status': status,'amt':amt})

    return render(request, 'VQA/Visual_Q&A.html', {'name': request.user.username.upper(), 'status': status,'amt':amt})



def bmi_calculator(request):
    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0
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

    return render(request, 'VQA/BMI_Calculator.html', {'name': request.user.username.upper(), 'status': status,'amt':amt})




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
    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0
    doctor = Doctor_register.objects.values_list('name', flat=True)
    if request.method == 'POST':
        print("Inside blog")
        name = request.user.username.upper()
        if Doctor_register.objects.filter(name=request.user.username).exists():
            consultant = Consultant.objects.filter(
                name=request.user.username).first()  # Get the first matching consultant
            if consultant:
                image = consultant.image
            else:
                image = "VQA/static/images/user.png"
        else:
            image = "VQA/static/images/user.png"
        post_image = request.FILES.get('post_image')
        print(post_image)
        description = request.POST.get('description')
        time = datetime.now().strftime('%d-%m-%y')

        print(image, post_image, name, description, time)

        blog_post = Blog(name=name, image=image, post_image=post_image, description=description, time=time)
        blog_post.save()

        return JsonResponse({'message':'yes','status':status, 'doctor': list(doctor)})

    return render(request, 'VQA/blog.html',
                  {'name': request.user.username.upper(), 'blog': Blog.objects.all().order_by('-id'),'status':status, 'doctor': list(doctor),'amt':amt})

def consultant(request):
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0
    rating = Feedback.objects.filter(name=request.user.username).all()
    if Doctor_register.objects.filter(name=request.user.username).exists():
        appointments = Appointment_status.objects.filter(doctor_name=request.user.username)
        fees = 0

        for appointment in appointments:
            fees += int(appointment.fee)

        return render(request, 'VQA/consultant.html', {'name': request.user.username.upper(), 'status': True, 'appointments': appointments,'fees':fees,'amt':amt})
    else:
        if request.method == 'POST':
            doctor_name = request.POST.get('doctor_name')
            name = request.POST.get('name1')
            mobile_number = request.POST.get('mobile_number')
            current_date_str = datetime.now().strftime('%d-%m-%Y')
            fee = request.POST.get('doctor_fee')
            status = "UNPAID"

            print(doctor_name, name, mobile_number, current_date_str, fee)
            val = Appointment_status(name=name, mobile=mobile_number, doctor_name=doctor_name, date=current_date_str, fee=fee,paid_status=status)
            val.save()
            return redirect('consultant')
    return render(request, 'VQA/consultant.html', {'name': request.user.username.upper(), 'consultant': Consultant.objects.all(),'rating':rating,'amt':amt})


def update_payment(request):
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        appointment = Appointment_status.objects.get(id=appointment_id)
        appointment.paid_status = 'PAID'
        appointment.save()
    return redirect('consultant')



def blooddonation(request):
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0

    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        bloodgroup = request.POST.get('bloodgroup')
        phonenumber = request.POST.get('phonenumber')
        address = request.POST.get('address')
        print(name, email, bloodgroup, phonenumber, address)
        val = BloodDonation(name=name, email=email, blood_group=bloodgroup, mobile=phonenumber, address=address)
        val.save()
        print(val)
        return render(request, 'VQA/blooddonation.html', {'name': request.user.username.upper(),'status':status,'amt':amt})
    return render(request, 'VQA/blooddonation.html', {'name': request.user.username.upper(),'status':status,'amt':amt})

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
    name_to_check = max(val)
    if User.objects.filter(username=name_to_check).exists():
        return render(request , 'vqa/index.html' , {"name" : max(val)})
    else:
        return render(request , 'vqa/register.html')

def imagecreation(request):
    if request.method == "POST":
        return redirect('imagecreation')

def doctor_register(request):
    if request.method == "POST":
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        pancard = request.POST.get('pancard')
        aadharcard = request.POST.get('aadharcard')
        specialist = request.POST.get('specialist')
        experience = request.POST.get('experience')
        hospital = request.POST.get('hospital')
        address = request.POST.get('address')
        password = request.POST.get('password')

        val = Doctor_register(name=name,age=age,gender=gender,email=email,mobile=mobile,pancard=pancard,aadharcard=aadharcard,specialist=specialist,experience=experience,hospital=hospital,address=address,password=password)
        val.save()
        user = User.objects.create_user(username=name, password=password)
        user.save()

        return render(request , 'vqa/register.html' , {'name' : request.user.username.upper()})
    return render(request , 'vqa/doctor_register.html' , {'name' : request.user.username.upper()})

def doctor_consultant(request):
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')
        address = request.POST.get('address')
        number = request.POST.get('number')
        specialist = request.POST.get('specialist')
        consultation_fee = request.POST.get('consultation_fee')
        print(name , address , number , specialist , consultation_fee)
        if image:
            my_model = Consultant(name=name,address=address,number=number,specialist=specialist,consultation_fee=consultation_fee)
            my_model.image = image
            my_model.save()
            print("saved")


        return render(request , 'vqa/consultant.html' , {'name' : request.user.username.upper(),'status': True})
    print("NOT SAVED")
    return render(request , 'vqa/doctor_consultant.html' , {'name' : request.user.username.upper()})


def appointment_status(request):
    det = Appointment_status.objects.filter(name=request.user.username).all()
    for doctor in det:
        feedback_exists = Feedback.objects.filter(doctor_name=doctor.doctor_name,name=request.user.username).exists()
        doctor.feedback_submitted = feedback_exists

    if Doctor_register.objects.filter(name=request.user.username).exists():
        status = True
    else:
        status = False

    feedback_submitted = Feedback.objects.filter(name=request.user.username).exists()
    try:
        user_wallet = User_Wallet.objects.get(name=request.user.username)
        amt = user_wallet.wallet_amount
    except User_Wallet.DoesNotExist:
        amt = 0


    return render(request , 'vqa/bookappointment.html',{'name' : request.user.username.upper(),'det':det,'status':status,'amt':amt})



def feedback_submit(request):
    if request.method == 'POST':
        doctor_name = request.POST.get('doctor_name')
        doctor_fee = request.POST.get('doctor_fee')
        feedback_text = request.POST.get('feedback_text')
        doctor_rating = request.POST.get('doctor_rating12')
        name = request.user.username
        dat = Feedback(doctor_name=doctor_name, fee=doctor_fee, feedback=feedback_text,rating=doctor_rating , name=name)
        dat.save()
        try:
            user_wallet = User_Wallet.objects.get(name=name)
        except User_Wallet.DoesNotExist:
            user_wallet = User_Wallet(name=name, wallet_amount=0)
            user_wallet.save()

            # Update wallet amount
        user_wallet.wallet_amount += 10
        user_wallet.save()


        # Add your logic for saving feedback here
        return redirect('appointment_status')
    return render(request, 'VQA/bookappointment.html', {'name': request.user.username.upper()})