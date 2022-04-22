from django.shortcuts import render
from rest_framework import generics
from .serializer import ServerSerializer
from .serializer import ServersReviewSerializer

from .models import Server

class ServerViewSet(generics.ListAPIView):

    queryset = Server.objects.all()
    serializer_class = ServerSerializer

class ServerAddView(generics.CreateAPIView):

    queryset = Server.objects.all()
    serializer_class = ServerSerializer

class ServerDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Server.objects.all()
    serializer_class = ServerSerializer

class ServerReviewsView(generics.ListAPIView):
    queryset = Server.objects.all()
    serializer_class = ServersReviewSerializer