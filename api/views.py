import operator

from django.core.cache import cache
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as django_login
from django.db.models import Max
from django.db.models import Q
from functools import reduce
from activities.models import Act
from common.models import MyUser
from post.models import Post
from comment.models import Comment
from django.views.decorators.csrf import csrf_exempt
#django rest framework
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import ActSerializer, PostAllSerializer, PostSerializer, UserSerializer, UserSettingsSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthenticatedOrCreate, IsActCreatorOrReadOnly
#django rest framework jwt
from rest_framework_jwt.settings import api_settings


class ActList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)
    queryset = Act.objects.all().order_by('-act_create_time')
    serializer_class = ActSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Act.objects.all().order_by('-act_create_time')
        post_queryset = Post.objects.all()
        act_type = self.request.query_params.get('act_type', None)
        act_author = self.request.query_params.get('act_author', None)
        act_post = self.request.query_params.get('act_post', None)
        act_id = self.request.query_params.get('act_id', None)
        if act_id is not None:
            queryset = queryset.filter(id=act_id)
        if act_type is not None:
            queryset = queryset.all().exclude(act_type=act_type)
        if act_author is not None:
            queryset = queryset.filter(user__user_name=act_author)
        if act_post is not None:
            post_object = post_queryset.filter(user__user_name=act_post)
            id_set = set()
            for post in post_object:
                id_set.add(post.act.id)
            query = reduce(operator.or_, (Q(id = item) for item in id_set))
            queryset = Act.objects.filter(query).order_by('-act_create_time')
        return queryset

class ActDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsAdminOrReadOnly)
    queryset = Act.objects.all()
    serializer_class = ActSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Post.objects.all()
    serializer_class = PostAllSerializer
    
    def create(self, request, *args, **kwargs):
        act_id = request.data.get('act')
        act = Act.objects.get(pk=act_id)
        if act.act_type == 0:
            if request.user != act.user:
                return Response(status=403)
        return super().create(request, args, kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Post.objects.all().order_by('-post_create_time')
        act_id = self.request.query_params.get('act_id', None)
        post_author = self.request.query_params.get('post_author', None)
        if act_id is not None:
            queryset = queryset.filter(act=act_id)
        if post_author is not None:
            queryset = queryset.filter(user__user_name=post_author)
        return queryset


 
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Post.objects.all()
        act_id = self.request.query_params.get('act_id', None)
       
        if act_id is not None:
            queryset = queryset.filter(act=act_id)

        return queryset


class CommentList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        reply_id = request.data.get("reply_id")
        cache.set(str(reply_id) + "_comments", "True")
        return super().create(request, args, kwargs)

    def get_queryset(self):
        queryset = Comment.objects.all().order_by("-comment_create_time")
        reply_id = self.request.query_params.get('reply_id', None)
       
        if reply_id is not None:
            queryset = queryset.filter(reply_id=reply_id)

        return queryset


class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserList(generics.ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrCreate,)
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_name = request.POST.get("user_name")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        new_user = authenticate(email=email, password=password)
        if new_user is not None:
            if new_user.is_active:
                #login after signup
                django_login(request, new_user)
        #if this is the first time user sign up and want to get token
        if "1wUnicooo" in request.META["HTTP_USER_AGENT"]:
            #payload = jwt_payload_handler(new_user)
            #token = jwt_enacode_handler(payload)
            #return Response(token, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = MyUser.objects.all()
    serializer_class = UserSettingsSerializer


