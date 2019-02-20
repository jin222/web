"""foodShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
import xadmin
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework_jwt.views import obtain_jwt_token
from django.views.generic import TemplateView

from foodShop.settings import MEDIA_ROOT
from goods.views import GoodsListViewSet, CategoryViewSet, BannerViewSet, IndexCategoryViewSet, IndexAdViewSet
from users.views import SmsCodeViewSet, UserViewSet
from user_operation.views import UserFavViewSet, UserLeavingMessageViewSet, UserAddressViewSet
from trade.views import ShopCartViewSet, OrderViewSet, AlipayView


router = DefaultRouter()
router.register(r'goods', GoodsListViewSet, base_name='goods')
router.register(r'categorys', CategoryViewSet, base_name='categorys')
router.register(r'banners', BannerViewSet, base_name='banners')
router.register(r'codes', SmsCodeViewSet, base_name='codes')
router.register(r'users', UserViewSet, base_name='users')
router.register(r'userfav', UserFavViewSet, base_name='userfav')
router.register(r'usermessage', UserLeavingMessageViewSet, base_name='usermessage')
router.register(r'useraddress', UserAddressViewSet, base_name='useraddress')
router.register(r'shopcarts', ShopCartViewSet, base_name='shopcarts')
router.register(r'orders', OrderViewSet, base_name='orders')
router.register(r'indexgoods', IndexCategoryViewSet, base_name='indexgoods')
router.register(r'indexad', IndexAdViewSet, base_name='indexad')

# goods_list = GoodsListViewSet.as_view({
#     'get': 'list',
# })

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),

    # 商品列表页
    # url(r'^goods/$', goods_list, name='goods_list'),
    url(r'^', include(router.urls)),
    url(r'^index/', TemplateView.as_view(template_name='index.html'), name='index'),


    url(r'doc/', include_docs_urls(title='生鲜鲜鲜')),
    # drf自带的token认证模式
    url(r'^api-token-auth/', views.obtain_auth_token),

    # drf的token认证模式
    url(r'^login/$', obtain_jwt_token),
    url(r'^alipay/return/', AlipayView.as_view(), name='alipay'),
    url('', include('social_django.urls', namespace='social'))

]
