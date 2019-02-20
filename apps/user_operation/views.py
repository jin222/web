from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .models import UserFav, UserLeavingMessage, UserAddress
from .serializers import UserFavSerializer, UserFavDetailSerializer, UserLeavingMessageSerializer, UserAddressSerializer
from utils.permissions import IsOwnerOrReadOnly


class UserFavViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
        list:
            获取用户的收藏
        create:
            添加收藏
        delete:
            删除收藏
        """
    # queryset = UserFav.objects.all()
    lookup_field = 'goods'
    # serializer_class = UserFavSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserFav.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserFavDetailSerializer
        elif self.action == 'create':
            return UserFavSerializer

        return UserFavSerializer

    # 重载CreateModelMixin的perform_create方法，实现点击收藏数增加
    # def perform_create(self, serializer):
    #     instance = serializer.save()
    #     goods = instance.goods
    #     goods.fav_num += 1
    #     goods.save()


class UserLeavingMessageViewSet(mixins.CreateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    list:
        获取用户留言
    create:
        添加留言
    delete:
        删除留言
    """
    serializer_class = UserLeavingMessageSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserLeavingMessage.objects.filter(user=self.request.user)


# 操作都包含了，直接用ModelViewSet
class UserAddressViewSet(viewsets.ModelViewSet):
    """
        list:
            获取用户收货地址
        create:
            添加收货地址
        delete:
            删除收货地址
        """
    serializer_class = UserAddressSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)