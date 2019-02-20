from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import mixins
from rest_framework.views import APIView
from datetime import datetime
from rest_framework.response import Response
from django.shortcuts import redirect

from utils.permissions import IsOwnerOrReadOnly
from .models import ShoppingCart, OrderInfo, OrderGoods
from .serializers import ShopCartSerializer, ShopCartDetailSerializer, OrderSerializer, OrderDetailSerializer
from foodShop.settings import private_key_path, ali_pub_key_path, ali_appid
from utils.alipay import AliPay


class ShopCartViewSet(viewsets.ModelViewSet):
    """
    list:
        获取购物车详情
    create:
        加入购物车
    delete:
        从购物车中删除
    """
    serializer_class = ShopCartSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    lookup_field = 'goods_id'

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ShopCartDetailSerializer
        elif self.action == 'create':
            return ShopCartSerializer

        return ShopCartSerializer


class OrderViewSet(mixins.CreateModelMixin,mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
        list:
            获取个人订单
        create:
            创建订单
        delete:
            删除订单
        """
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        else:
            return OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        shop_carts = ShoppingCart.objects.filter(user=self.request.user, selected=True)
        for shop_cart in shop_carts:
            order_goods = OrderGoods()
            order_goods.goods = shop_cart.goods
            order_goods.goods_num = shop_cart.nums
            order_goods.order = order
            order_goods.save()
        shop_carts.delete()
        return order


class AlipayView(APIView):
    def get(self, request):
        processed_dict = {}
        for key, value in request.GET.items():
            processed_dict[key] = value

        sign = processed_dict.pop('sign', None)

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

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_orders = OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            response = redirect('index')
            response.set_cookie('nextPath', 'pay', max_age=2)
            return response
        else:
            response = redirect('index')
            return response

    def post(self, request):
        processed_dict = {}
        for key, value in request.POST.items():
            processed_dict[key] = value

        sign = processed_dict.pop('sign', None)

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

        verify_re = alipay.verify(processed_dict, sign)

        if verify_re is True:
            order_sn = processed_dict.get('out_trade_no', None)
            trade_no = processed_dict.get('trade_no', None)
            trade_status = processed_dict.get('trade_status', None)

            existed_orders =OrderInfo.objects.filter(order_sn=order_sn)
            for existed_order in existed_orders:
                order_goods = existed_order.goods.all()
                for order_good in order_goods:
                    goods = order_good.goods
                    goods.sold_num += order_good.goods_num
                    goods.save()
                existed_order.pay_status = trade_status
                existed_order.trade_no = trade_no
                existed_order.pay_time = datetime.now()
                existed_order.save()

            return Response('success')