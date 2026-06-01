from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    path(route='', view=views.index, name='index'),
    path('<int:course_id>/enroll/', views.enroll, name='enroll'),
    path('<int:course_id>/', views.course_details, name='course_details'),
    path('<int:course_id>/submit/', views.submit, name='submit'),
    path('<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='show_exam_result'),
    path('registration/', views.registration_request, name='registration'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
]