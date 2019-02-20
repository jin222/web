from rest_framework import serializers
from goods.models import Goods, GoodsCategory, Banner, GoodsImage, GoodsCategoryBrand, IndexAd
from django.db.models import Q
# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Goods.objects.create(**validated_data)


class GoodsCategorySerializer3(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsCategorySerializer2(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializer3(many=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):
    sub_cat = GoodsCategorySerializer2(many=True)
    class Meta:
        model = GoodsCategory
        fields = '__all__'


class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImage
        fields = ('image',)


class GoodsSerializer(serializers.ModelSerializer):
    category = GoodsCategorySerializer()
    images = GoodsImageSerializer(many=True)
    class Meta:
        model = Goods
        fields = '__all__'
        # fields = ('name', 'click_num', 'market_price', 'add_time')


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = '__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategoryBrand
        fields = '__all__'


class IndexAdSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)
    class Meta:
        model = IndexAd
        fields = '__all__'


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True)
    goods = serializers.SerializerMethodField()
    sub_cat = GoodsCategorySerializer2(many=True)
    ad = IndexAdSerializer(many=True)

    def get_goods(self, obj):
        all_goods = Goods.objects.filter(Q(category_id=obj.id)|Q(category__parent_category_id=obj.id)|Q(
                category__parent_category__parent_category_id=obj.id)).order_by('-sold_num')[:6]
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request':self.context['request']})
        return goods_serializer.data

    class Meta:
        model = GoodsCategory
        fields = '__all__'