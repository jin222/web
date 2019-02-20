from rest_framework import serializers
import re
from datetime import datetime, timedelta
from rest_framework.validators import UniqueValidator

from .models import VerifyCode
from foodShop.settings import REGEX_MOBILE
# get_user_model方法会去setting中找AUTH_USER_MODEL
from django.contrib.auth import get_user_model
User = get_user_model()


class SmsSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def validate_mobile(self, mobile):
        """
        验证手机号码
        :param mobile:
        :return:
        """
        # 手机号是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError('用户已存在001')

        # 手机号是否合法
        if not re.match(REGEX_MOBILE, mobile):
            raise serializers.ValidationError('手机号码非法')

        one_minutes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)

        if VerifyCode.objects.filter(add_time__gt=one_minutes_ago, mobile=mobile):
            raise serializers.ValidationError('距离上一次发送未超过一分钟')
        return mobile


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'gender', 'birthday', 'email', 'mobile')


class UserRegSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4, min_length=4, write_only=True, label='验证码', help_text='验证码',
                                 error_messages={
                                     'blank': '请输入验证码',
                                     'required': '请输入验证码',
                                     'max_length': '验证码格式错误',
                                     'min_length': '验证码格式错误',
                                 })
    username = serializers.CharField(required=True, allow_blank=False, label='用户名',
                                     validators=[UniqueValidator(queryset=User.objects.all(),message='用户已存在')])
    password = serializers.CharField(style={'input_type':'password'}, label='密码', write_only=True)

    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    print('开始验证code')

    def validate_code(self, code):
        print(code)
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if verify_records:
            last_record = verify_records[0]
            five_minutes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_minutes_ago > last_record.add_time:
                raise serializers.ValidationError('验证码过期')
            if last_record.code != code:
                raise serializers.ValidationError('验证码错误')
        else:
            raise serializers.ValidationError("请确认账号")

    def validate(self, attrs):
        attrs['mobile'] = attrs['username']
        del attrs['code']
        return attrs

    class Meta:
        model = User
        fields = ('username', 'code', 'mobile', 'password')