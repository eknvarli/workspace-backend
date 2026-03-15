from django.contrib import admin
from .models import CustomUser, Team, Note, Customer, Todo, Project, ProjectNote, ProjectFile

@admin.action(description='Seçili kullanıcıları onayla')
def approve_users(modeladmin, request, queryset):
    queryset.update(is_approved=True)

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_approved', 'is_staff', 'team']
    list_filter = ['is_approved', 'is_staff', 'team']
    actions = [approve_users]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Team)
admin.site.register(Note)
admin.site.register(Customer)
admin.site.register(Todo)
admin.site.register(Project)
admin.site.register(ProjectNote)
admin.site.register(ProjectFile)
