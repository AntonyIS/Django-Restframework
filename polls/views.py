from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework import viewsets
from rest_framework import generics
from .models import Poll, Choice, Vote
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer
from django.contrib.auth import authenticate


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def destroy(self, request, *args, **kwargs):
        polls = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == polls.created_by:
            raise PermissionDenied("You cannot delete this poll")
        return super().destroy(self,request,*args,**kwargs)


class PollDetail(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class ChoiceList(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])
        return queryset
    serializer_class = ChoiceSerializer

    def post(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == poll.created_by:
            raise PermissionDenied("You cannot create choices for this poll.")
        return super().post(request, *args,**kwargs)


class CreateVote(APIView):
    serializer_class = VoteSerializer

    def post(self,request,pk,choice_pk):
        voted_by = request.data.get("voted_by")
        data = {
            "choice":choice_pk,
            "poll":pk,
            "voted_by":voted_by
        }
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class LoginView(APIView):
    permission_classes = ()

    def post(self,request):
        user = authenticate (
            username=request.data.get('username'),
            password=request.data.get('password'),
        )
        if user:
            return Response({
                "token":user.auth_token.key
            })
        else:
            return Response({"error": "Wrong Credential"},status= status.HTTP_400_BAD_REQUEST)
