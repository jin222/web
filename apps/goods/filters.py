from django_filters import rest_framework as filters
from .models import Goods
from django.db.models import Q


class GoodsFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="shop_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="shop_price", lookup_expr='lte')
    # name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    top_category = filters.NumberFilter(method='top_category_filter')

    def top_category_filter(self, queryset, name, value):
        return queryset.filter(Q(category_id=value)|Q(category__parent_category_id=value)|Q(category__parent_category__parent_category_id=value))
    class Meta:
        model = Goods
        fields = ['min_price', 'max_price', 'top_category', 'is_hot', 'is_new']

