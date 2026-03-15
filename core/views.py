from rest_framework import status, views, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import (
    UserSerializer, RegisterSerializer, SetupSerializer,
    TeamSerializer, NoteSerializer, CustomerSerializer, TodoSerializer,
    ProjectSerializer, ProjectNoteSerializer, ProjectFileSerializer
)
from .models import Team, Note, Customer, Todo, Project, ProjectNote, ProjectFile
from django.db.models import Q

User = get_user_model()

class TodoViewSet(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response([])
        todos = Todo.objects.filter(team=request.user.team)
        return Response(TodoSerializer(todos, many=True).data)

    def post(self, request):
        if not request.user.team:
            return Response({'error': 'Önce bir ekip oluşturmalısınız.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['team'] = request.user.team.id
        serializer = TodoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodoDetailView(views.APIView):
    def get_object(self, pk, team):
        try:
            return Todo.objects.get(pk=pk, team=team)
        except Todo.DoesNotExist:
            return None

    def put(self, request, pk):
        todo = self.get_object(pk, request.user.team)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TodoSerializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        todo = self.get_object(pk, request.user.team)
        if not todo:
            return Response(status=status.HTTP_404_NOT_FOUND)
        todo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DashboardStatsView(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response({'error': 'Ekip yok.'}, status=status.HTTP_404_NOT_FOUND)
        
        team = request.user.team
        member_count = team.members.count()
        total_todos = team.todos.count()
        completed_todos = team.todos.filter(status='Tamamlandı').count()
        
        last_notes = Note.objects.filter(team=team).order_by('-created_at')[:5]
        active_projects = Project.objects.filter(team=team, status='Aktif')
        
        return Response({
            'team_name': team.name,
            'member_count': member_count,
            'total_todos': total_todos,
            'completed_todos': completed_todos,
            'last_notes': NoteSerializer(last_notes, many=True).data,
            'active_projects': ProjectSerializer(active_projects, many=True).data
        })

class TeamMembersView(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response([])
        members = User.objects.filter(team=request.user.team)
        return Response(UserSerializer(members, many=True).data)

class SetupStatusView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        setup_required = not User.objects.filter(is_superuser=True).exists()
        return Response({'setup_required': setup_required})

class InitialSetupView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if User.objects.filter(is_superuser=True).exists():
            return Response({'error': 'Kurulum zaten tamamlanmış.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SetupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if not user.is_approved:
                return Response({'error': 'Hesabınız onay bekliyor. Lütfen yöneticinin onaylamasını bekleyin.'}, status=status.HTTP_403_FORBIDDEN)
            
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Hatalı kullanıcı adı veya şifre.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Kayıt başarılı. Lütfen yönetici onayını bekleyin.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(views.APIView):
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Başarıyla çıkış yapıldı.'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Çıkış yapılamadı.'}, status=status.HTTP_400_BAD_REQUEST)

class TeamViewSet(views.APIView):
    def get(self, request):
        if not request.user.team:
            team = Team.objects.first()
            if team:
                request.user.team = team
                request.user.save()
                return Response(TeamSerializer(team).data)
            return Response({'message': 'Ekip bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TeamSerializer(request.user.team).data)

    def post(self, request):
        if Team.objects.exists():
            return Response({'error': 'Sistemde zaten bir ekip mevcut.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            request.user.team = team
            request.user.save()
            return Response(TeamSerializer(team).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteViewSet(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response([])
        notes = Note.objects.filter(team=request.user.team)
        return Response(NoteSerializer(notes, many=True).data)

    def post(self, request):
        if not request.user.team:
            return Response({'error': 'Önce bir ekip oluşturmalısınız.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['team'] = request.user.team.id
        data['created_by'] = request.user.id
        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteDetailView(views.APIView):
    def get_object(self, pk, team):
        try:
            return Note.objects.get(pk=pk, team=team)
        except Note.DoesNotExist:
            return None

    def put(self, request, pk):
        note = self.get_object(pk, request.user.team)
        if not note:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        note = self.get_object(pk, request.user.team)
        if not note:
            return Response(status=status.HTTP_404_NOT_FOUND)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerViewSet(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response([])
        customers = Customer.objects.filter(team=request.user.team)
        return Response(CustomerSerializer(customers, many=True).data)

    def post(self, request):
        if not request.user.team:
            return Response({'error': 'Önce bir ekip oluşturmalısınız.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['team'] = request.user.team.id
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectViewSet(views.APIView):
    def get(self, request):
        if not request.user.team:
            return Response([])
        projects = Project.objects.filter(team=request.user.team)
        return Response(ProjectSerializer(projects, many=True).data)

    def post(self, request):
        if not request.user.team:
            return Response({'error': 'Önce bir ekip oluşturmalısınız.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['team'] = request.user.team.id
        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetailView(views.APIView):
    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, team=request.user.team)
            notes = ProjectNote.objects.filter(project=project)
            files = ProjectFile.objects.filter(project=project)
            return Response({
                'project': ProjectSerializer(project).data,
                'notes': ProjectNoteSerializer(notes, many=True).data,
                'files': ProjectFileSerializer(files, many=True).data
            })
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProjectNoteView(views.APIView):
    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, team=request.user.team)
            data = request.data.copy()
            data['project'] = project.id
            data['created_by'] = request.user.id
            serializer = ProjectNoteSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProjectNoteDetailView(views.APIView):
    def delete(self, request, pk):
        try:
            note = ProjectNote.objects.get(pk=pk, created_by=request.user)
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectNote.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProjectFileView(views.APIView):
    def post(self, request, pk):
        try:
            project = Project.objects.get(pk=pk, team=request.user.team)
            data = request.data.copy()
            data['project'] = project.id
            data['uploaded_by'] = request.user.id
            serializer = ProjectFileSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PendingUsersView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_approved=False, is_superuser=False)
        return Response(UserSerializer(users, many=True).data)

class ApproveUserView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_approved = True
            user.save()
            return Response({'message': 'Kullanıcı onaylandı.'})
        except User.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

class RejectUserView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response({'message': 'Resmiyet iptal edildi.'})
        except User.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

class GlobalSearchView(views.APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query or not request.user.team:
            return Response({'notes': [], 'customers': [], 'projects': []})
        
        team = request.user.team

        notes = Note.objects.filter(
            Q(team=team) & (Q(title__icontains=query) | Q(content__icontains=query))
        ).distinct()

        customers = Customer.objects.filter(
            Q(team=team) & (Q(name__icontains=query) | Q(company__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
        ).distinct()

        projects = Project.objects.filter(
            Q(team=team) & (Q(name__icontains=query) | Q(description__icontains=query))
        ).distinct()

        return Response({
            'notes': NoteSerializer(notes, many=True).data,
            'customers': CustomerSerializer(customers, many=True).data,
            'projects': ProjectSerializer(projects, many=True).data
        })
