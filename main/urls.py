from django.urls import path, include
from .views import (
    about_view, register_view, login_view, logout_view,
    dashboard_view, profile_view, create_project,
    project_list, project_detail, edit_project,
    delete_project, accept_offer, leave_review,
)

urlpatterns = [
    path('api/', include('main.urls_api')),
    path('', dashboard_view, name='dashboard'),
    path('about/', about_view, name='about'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/<int:user_id>/', profile_view, name='profile_view'),
    path('projects/', project_list, name='project_list'),
    path('projects/create/', create_project, name='create_project'),
    path('projects/<int:pk>/', project_detail, name='project_detail'),
    path('projects/<int:pk>/edit/', edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', delete_project, name='delete_project'),
    path('offers/<int:pk>/accept/', accept_offer, name='accept_offer'),
    path('review/<int:user_id>/<int:project_id>/', leave_review, name='leave_review'),
]
