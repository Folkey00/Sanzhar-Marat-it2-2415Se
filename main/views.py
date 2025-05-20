from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Avg, Q

from .forms import (
    RegisterForm, LoginForm, ProjectForm, OfferForm,
    ReviewForm, CommentForm, MessageForm
)
from .models import Project, Offer, Review, User, Comment


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect('profile')
    else:
        form = RegisterForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'welcome.html')


@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@login_required
def profile_view(request, user_id=None):
    user = get_object_or_404(User, pk=user_id) if user_id else request.user
    reviews = Review.objects.filter(reviewed=user)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    has_shared_project = Project.objects.filter(
        Q(client__in=[request.user, user]) & Q(executor__in=[request.user, user])
    ).exists() if user != request.user else False

    return render(request, 'profile.html', {
        'user_profile': user,
        'average_rating': round(average_rating, 1),
        'reviews': reviews,
        'can_review': has_shared_project,
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            if project.deadline < timezone.now().date():
                messages.error(request, "Дедлайн не может быть в прошлом.")
            else:
                project.client = request.user
                project.save()
                return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})


def project_list(request):
    search_query = request.GET.get('q')
    min_budget = request.GET.get('min_budget')
    max_budget = request.GET.get('max_budget')

    projects = Project.objects.all()

    if search_query:
        projects = projects.filter(title__icontains=search_query)
    if min_budget:
        projects = projects.filter(budget__gte=min_budget)
    if max_budget:
        projects = projects.filter(budget__lte=max_budget)

    return render(request, 'project_list.html', {
        'projects': projects,
        'search_query': search_query,
        'min_budget': min_budget,
        'max_budget': max_budget
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    offers = project.offers.all()
    comments = project.comments.all().order_by('-created_at')

    offer_form = None
    comment_form = CommentForm()

    if request.user.is_authenticated and request.user != project.client:
        if request.method == 'POST':
            offer_form = OfferForm(request.POST)
            comment_form = CommentForm(request.POST)
            if offer_form.is_valid():
                offer = offer_form.save(commit=False)
                offer.project = project
                offer.freelancer = request.user
                offer.save()
                messages.success(request, "Отклик отправлен успешно.")
                return redirect('project_detail', pk=pk)
            elif comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.project = project
                comment.author = request.user
                comment.save()
                return redirect('project_detail', pk=pk)
        else:
            offer_form = OfferForm()

    can_chat = project.executor and request.user in [project.client, project.executor]

    return render(request, 'project_detail.html', {
        'project': project,
        'offers': offers,
        'comments': comments,
        'offer_form': offer_form,
        'comment_form': comment_form,
        'can_chat': can_chat,
    })


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            if form.cleaned_data['deadline'] < timezone.now().date():
                messages.error(request, "Дедлайн не может быть в прошлом.")
            else:
                form.save()
                return redirect('project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'edit_project.html', {'form': form, 'project': project})


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.client != request.user:
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('project_list')

    return render(request, 'delete_project.html', {'project': project})


@login_required
def accept_offer(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    project = offer.project

    if request.user != project.client:
        return redirect('project_detail', pk=project.pk)

    project.executor = offer.freelancer
    project.save()

    messages.success(request, f"Вы назначили {offer.freelancer.username} исполнителем проекта!")
    return redirect('project_chat', pk=project.pk)


@login_required
def leave_review(request, user_id, project_id):
    reviewed_user = get_object_or_404(User, pk=user_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewed = reviewed_user
            review.project = project
            review.save()
            messages.success(request, "Отзыв успешно оставлен.")
            return redirect('profile', user_id=reviewed_user.id)
    else:
        form = ReviewForm()

    return render(request, 'leave_review.html', {
        'form': form,
        'reviewed_user': reviewed_user,
        'project': project
    })


def about_view(request):
    return render(request, 'about.html')


@login_required
def my_offers_view(request):
    offers = Offer.objects.filter(freelancer=request.user).select_related('project').order_by('-created_at')
    return render(request, 'my_offers.html', {'offers': offers})


@login_required
def project_chat(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not project.executor:
        messages.error(request, "Чат доступен только после назначения исполнителя.")
        return redirect('project_detail', pk=pk)

    if request.user not in [project.client, project.executor]:
        return redirect('dashboard')

    messages_qs = project.messages.filter(
        sender__in=[project.client, project.executor],
        receiver__in=[project.client, project.executor]
    ).order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.project = project
            msg.sender = request.user
            msg.receiver = (
                project.executor if request.user == project.client else project.client
            )
            msg.save()
            messages.success(request, "Сообщение отправлено!")
            return redirect('project_chat', pk=pk)
    else:
        form = MessageForm()

    return render(request, 'chat.html', {
        'project': project,
        'messages': messages_qs,
        'form': form
    })
