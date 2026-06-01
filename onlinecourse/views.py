from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import logging

from .models import Course, Lesson, Enrollment, Question, Choice, Submission

logger = logging.getLogger(__name__)


def registration_request(request):
    from django.contrib.auth.forms import UserCreationForm
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['form'] = form
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def index(request):
    context = {}
    if not request.user.is_authenticated:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        courses = Course.objects.all()
        enrolled_courses = request.user.enrollment_set.all()
        for course in courses:
            if enrolled_courses.filter(course_id=course.id):
                course.is_enrolled = True
        context['course_list'] = courses
        return render(request, 'onlinecourse/course_list_bootstrap.html', context)


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    is_enrolled = Enrollment.objects.filter(user=user, course=course).exists()
    if not is_enrolled and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


def course_details(request, course_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    context['course'] = course
    return render(request, 'onlinecourse/course_details_bootstrap.html', context)


@login_required
def submit(request, course_id):
    user = request.user
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    submitted_answers = []
    for key, values in request.POST.items():
        if key.startswith('choice'):
            for value in request.POST.getlist(key):
                submitted_answers.append(value)
    selected_ids = [int(v) for v in submitted_answers]
    selected_choices = Choice.objects.filter(id__in=selected_ids)
    submission.choices.set(selected_choices)
    submission.save()
    return HttpResponseRedirect(
        reverse('onlinecourse:show_exam_result', args=(course_id, submission.id))
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_ids = submission.choices.values_list('id', flat=True)
    total_score = 0
    for question in course.question_set.all():
        if question.is_get_score(selected_ids):
            total_score += question.grade
    context['course'] = course
    context['submission'] = submission
    context['selected_ids'] = selected_ids
    context['total_score'] = total_score
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)