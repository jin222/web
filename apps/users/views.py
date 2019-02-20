from django.shortcuts import render
from rest_framework.mixins import CreateModelMixin
from rest_framework import mixins
from rest_framework import permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from random import choice
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler

from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from utils.yunpian import YunPian
from .models import VerifyCode
from django.contrib.auth import get_user_model
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 用户名和手机都能登录
            user = User.objects.get(
                Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                print('success')
                return user
        except Exception as e:
            return None


class SmsCodeViewSet(CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = '1234567890'
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return ''.join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data['mobile']
        print(mobile)
        code = self.generate_code()
        yun_pian = YunPian()
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        # 根据短信接口平台不同，发送成功后返回的信息中code也不同，云片网为0，互亿无线为2
        if sms_status['code'] != 2:
            print('jiehuoaaaa')
            return Response({
                'mobile': '验证码获取失败'
                # 'mobile': sms_status['msg']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 发送成功验证码后，往表里存入code和mobile
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                'mobile': mobile
            }, status=status.HTTP_201_CREATED)


class UserViewSet(CreateModelMixin,mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    print('进入用户创建部分')
    serializer_class = UserRegSerializer
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserRegSerializer
        return UserDetailSerializer


    def get_object(self):
        return self.request.user

    # 重写，根据不同操作动态选择权限操作
    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            return []
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 把序列化后的数据赋值给user
        user = self.perform_create(serializer)
        re_dict = serializer.data
        # 实例化payload
        payload = jwt_payload_handler(user)
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['name'] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()