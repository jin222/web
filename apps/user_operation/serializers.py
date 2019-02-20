from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import UserFav, UserLeavingMessage, UserAddress
from goods.serializers import GoodsSerializer


class UserFavDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer()

    class Meta:
        model = UserFav
        fields = ('goods', 'id', 'add_time')


class UserFavSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserFav
        # 设置关联唯一，也可在model中设施unique  
        validators = [
            UniqueTogetherValidator(
                queryset=UserFav.objects.all(),
                fields=('user', 'goods'),
                message='已收藏'
            )
        ]
        fields = ('user', 'goods', 'id')


class UserLeavingMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = UserLeavingMessage
        fields = ('user', 'message_type', 'subject', 'message', 'file', 'id', 'add_time')


class UserAddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserAddress
        fields = ('user', 'province', 'city', 'district', 'address', 'signer_name', 'signer_mobile', 'id',)