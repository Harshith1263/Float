from django.shortcuts import redirect, render
from django.db.models.signals import post_save
from django.contrib.auth.models import User

import courses
from .forms import CourseCreationForm , CourseJoinForm
from .models import Course #, Student , Instructor
import random
# Create your views here.



def generate_code(): #function to generate random course code.
    s = ""
    for i in range(0,6):
        c = random.randint(65,90)
        s += chr(c)
    return s

'''--------------------------------------------------------------'''

def course_info(request):

    if not request.user.is_authenticated:
        return redirect('login')

    u = User.objects.get(pk = request.user.pk )
    args = {
        'icourses': u.stud_courses.all(),
        'scourses': u.ins_courses.all(),
    }

    return render(request,'courses/home.html',args)

def create(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = CourseCreationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            course_name = form.cleaned_data['name']
            code = generate_code()

            e = Course.objects.all().filter(joincode = code).count()
            while e != 0:
                code = generate_code()
                e = Course.objects.all().filter(joincode = code).count()

            e = Course.objects.all().filter(name = course_name).count()
            if( e != 0): #Name already exists.
                args = {'form': form, 'wrong': True}
                return render(request, 'courses/create.html', args)

            c = Course.objects.create(instructor = request.user)
            c.name = course_name
            c.joincode = code
            c.save()

            return redirect('CourseHome')

    else:
        form = CourseCreationForm()

    return render(request, 'courses/create.html', {'form': form, 'wrong': False})
'---------------------------------------------------------------------------'

def join(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = CourseJoinForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            code = form.cleaned_data['code']
            e = Course.objects.all().filter(joincode = code).count()

            if( e == 0):  #incorrect course code.
                args = {'form': form, 'wrong': True}
                return render(request, 'courses/join.html', args)
            
            c = Course.objects.get(joincode = code)
            c.students.add(request.user)
            c.save()

            return redirect('CourseHome')

    else:
        form = CourseJoinForm()

    return render(request, 'courses/join.html', {'form': form ,'wrong': False })

'--------------------------------------------------------------'

def course(request,course_id):
        c = Course.objects.get(pk = course_id)
        args = {
            'Instructor': c.instructor,
            'Students': c.students,
            'course': c
        }
        return render(request,'courses/coursepage.html',args)