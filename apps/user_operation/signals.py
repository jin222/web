# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import get_user_model
# User = get_user_model()
#
# @receiver(post_save, sender=User)
# def create_user(sender, instance=None, created=False, **kwargs):
#     if created:
#         password =instance.password
#         instance.set_password(password)
#         instance.save()


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
from user_operation.models import UserFav

# post_save:接收信号的方式，在save后
# sender: 接收信号的model
@receiver(post_save, sender=UserFav)
def create_userFav(sender, instance=None, created=False, **kwargs):
    # 是否新建，因为update的时候也会进行post_save
    if created:
        goods = instance.goods
        goods.fav_num += 1
        goods.save()


@receiver(post_delete, sender=UserFav)
def delete_userFav(sender, instance=None, created=False, **kwargs):
        goods = instance.goods
        goods.fav_num -= 1
        goods.save()