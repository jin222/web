from rest_framework import serializers
import time
from random import Random
from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.models import Goods
from goods.serializers import GoodsSerializer
from foodShop.settings import private_key_path, ali_pub_key_path, ali_appid
from utils.alipay import AliPay

class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = ('goods', 'nums', 'selected')


class ShopCartSerializer(serializers.Serializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        'min_value':'商品数量不能小于1',
                                        'required':'请选择购买数量'
                                    })
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=Goods.objects.all())
    selected = serializers.BooleanField()

    def create(self, validated_data):
        user = self.context['request'].user
        nums = validated_data['nums']
        goods = validated_data['goods']
        # selected = validated_data['selected'] or False

        existed = ShoppingCart.objects.filter(user=user, goods=goods)

        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)

        return existed

    def update(self, instance, validated_data):
        if 'nums' in validated_data:
            instance.nums = validated_data['nums']
        if 'selected' in validated_data:
            instance.selected = validated_data['selected']
        instance.save()
        return instance


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    pay_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = AliPay(
            # 沙箱里面的appid值
            appid=ali_appid,
            # notify_url是异步的url
            app_notify_url="http://39.107.94.185:8000/alipay/return/",
            # 我们自己商户的密钥
            app_private_key_path=private_key_path,
            # 支付宝的公钥
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # debug为true时使用沙箱的url。如果不是用正式环境的url
            debug=True,  # 默认False,
            return_url="http://39.107.94.185:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            # 订单标题
            subject=obj.order_sn,
            # 我们商户自行生成的订单号
            out_trade_no=obj.order_sn,
            # 订单金额
            total_amount=obj.order_mount,
            # 成功付款后跳转到的页面，return_url同步的url
            # return_url="http://39.107.94.185:8000/alipay/return/"
        )
        # 将生成的请求字符串拿到我们的url中进行拼接
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url
    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    order_sn = serializers.CharField(read_only=True)
    nonce_str = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    pay_status = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    alipay_url = serializers.SerializerMethodField(read_only=True)

    def get_alipay_url(self, obj):
        alipay = AliPay(
            # 沙箱里面的appid值
            appid=ali_appid,
            # notify_url是异步的url
            app_notify_url="http://39.107.94.185:8000/alipay/return/",
            # 我们自己商户的密钥
            app_private_key_path=private_key_path,
            # 支付宝的公钥
            alipay_public_key_path=ali_pub_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            # debug为true时使用沙箱的url。如果不是用正式环境的url
            debug=True,  # 默认False,
            return_url="http://39.107.94.185:8000/alipay/return/"
        )
        url = alipay.direct_pay(
            # 订单标题
            subject=obj.order_sn,
            # 我们商户自行生成的订单号
            out_trade_no=obj.order_sn,
            # 订单金额
            total_amount=obj.order_mount,
            # 成功付款后跳转到的页面，return_url同步的url
            # return_url="http://39.107.94.185:8000/alipay/return/"
        )
        # 将生成的请求字符串拿到我们的url中进行拼接
        re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)

        return re_url

    def generate_order_sn(self):
        random_ins = Random()
        order_sn = '{time_str}{userid}{ranstr}'.format(time_str=time.strftime('%Y%m%d%H%M%S'),
                                                       userid=self.context['request'].user.id,
                                                       ranstr=random_ins.randint(10, 99))
        return order_sn

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'