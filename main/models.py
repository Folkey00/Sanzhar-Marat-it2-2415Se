from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_freelancer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username


class Project(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    executor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='executed_projects'
    )

    def __str__(self):
        return self.title


class Offer(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='offers')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal_text = models.TextField()
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Offer by {self.freelancer} for {self.project}'


class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.reviewer} → {self.reviewed} ({self.rating})'

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username}: {self.text[:30]}'


