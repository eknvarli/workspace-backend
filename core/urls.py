from django.urls import path
from .views import (
    SetupStatusView, InitialSetupView, LoginView, RegisterView, LogoutView,
    TeamViewSet, NoteViewSet, NoteDetailView, CustomerViewSet,
    TodoViewSet, TodoDetailView, DashboardStatsView, TeamMembersView,
    PendingUsersView, ApproveUserView, RejectUserView,
    ProjectViewSet, ProjectDetailView, ProjectNoteView, ProjectNoteDetailView, ProjectFileView,
    GlobalSearchView
)

urlpatterns = [
    path('search-global/', GlobalSearchView.as_view()),
    path('setup-status/', SetupStatusView.as_view()),
    path('setup/', InitialSetupView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('team/', TeamViewSet.as_view()),
    path('notes/', NoteViewSet.as_view()),
    path('notes/<int:pk>/', NoteDetailView.as_view()),
    path('customers/', CustomerViewSet.as_view()),
    path('todos/', TodoViewSet.as_view()),
    path('todos/<int:pk>/', TodoDetailView.as_view()),
    path('stats/', DashboardStatsView.as_view()),
    path('members/', TeamMembersView.as_view()),
    path('pending-users/', PendingUsersView.as_view()),
    path('approve-user/<int:pk>/', ApproveUserView.as_view()),
    path('reject-user/<int:pk>/', RejectUserView.as_view()),
    path('projects/', ProjectViewSet.as_view()),
    path('projects/<int:pk>/', ProjectDetailView.as_view()),
    path('projects/<int:pk>/notes/', ProjectNoteView.as_view()),
    path('project-notes/<int:pk>/', ProjectNoteDetailView.as_view()),
    path('projects/<int:pk>/files/', ProjectFileView.as_view()),
]
