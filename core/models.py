from django.contrib.auth.models import AbstractUser
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='notes')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Customer(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, default='Potansiyel')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='customers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class Todo(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_todos')
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, default='Yapılacak')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='todos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=50, default='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

class ProjectNote(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.project.name}"

    class Meta:
        ordering = ['-created_at']

class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='project_files/')
    name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-uploaded_at']
