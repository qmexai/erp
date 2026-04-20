from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # CEO/HR can see all, Dept Head can see their dept, Employee sees self
        user = request.user
        if user.role in ['CEO', 'HR']:
            queryset = User.objects.all()
        elif user.role == 'Dept Head':
            queryset = User.objects.filter(department=user.department)
        else:
            queryset = User.objects.filter(id=user.id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
