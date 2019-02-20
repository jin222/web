from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .serializers import GoodsSerializer, GoodsCategorySerializer, \
                        BannerSerializer, IndexCategorySerializer,\
                        IndexAdSerializer
from .models import Goods, GoodsCategory, Banner, IndexAd
from .filters import GoodsFilter

# class GoodsListView(APIView):
#     """
#     List all goods.
#     """
#     def get(self, request, format=None):
#         goods = Goods.objects.all()[:10]
#         goods_serializer = GoodsSerializer(goods, many=True)
#         return Response(goods_serializer.data)
#
#     def post(self, request, format=None):
#         serializer = GoodsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class GoodsListView(mixins.ListModelMixin, generics.GenericAPIView):
#     queryset = Goods.objects.all()[:10]
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)


class GoodsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    page_query_param = 'p'
    max_page_size = 100


# class GoodsListView(generics.ListAPIView):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#     pagination_class = GoodsPagination

class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        商品展示列表
    """
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination
    throttle_classes = (AnonRateThrottle, UserRateThrottle)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filter_fields = ('name', 'shop_price')
    filter_class = GoodsFilter
    search_fields = ('name', 'goods_brief', 'goods_desc')
    ordering_fields = ('market_price', 'shop_price', 'sold_num')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        商品分类列表数据
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = GoodsCategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id',)
    # filter_class = GoodsFilter
    # search_fields = ('name', 'goods_brief', 'goods_desc')
    # ordering_fields = ('market_price', 'goods_num')


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Banner.objects.all().order_by('index')
    serializer_class = BannerSerializer


class IndexCategoryViewSet(CacheResponseMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=['蔬菜水果', '生鲜食品'])
    serializer_class = IndexCategorySerializer


class IndexAdViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = IndexAd.objects.all()
    serializer_class = IndexAdSerializer