from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class ImagerProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')

    profile_picture = models.ImageField(null=True, blank=True, upload_to='images')
    phone_number = models.CharField(max_length=15)  # X(XXX) XXX-XXXX
    birthday = models.DateField(blank=True)

    phone_privacy = models.BooleanField(default=False)
    birthday_privacy = models.BooleanField(default=False)
    picture_privacy = models.BooleanField(default=False)
    name_privacy = models.BooleanField(default=False)
    email_privacy = models.BooleanField(default=False)

    # relationship = models.ManyToManyField(User,
    #                                       symetrical=False,
    #                                       related_name='+',
    #                                       through='imager_users.Relationship'
    #                                       )

    # To find following
    # return Relationship.objects.filter(left=me, status__in=(1, 3))

    # To find followers
    # return Relationship.objects.filter(right=me, status__in=(1, 3))

    def __str__(self):
        return "User: {}".format(self.user.username)

    def is_active(self):
        return self.user.is_active()

    def follow(self, other):
        pass

    def unfollow(self, other):
        pass

    @classmethod
    def active(self):
        qs = self.get_queryset()
        return qs.filter(user__is_active=True)

# create profile
# delete user

# post_save.connect(create_profile, sender=User)
# pre_delete.conect(delete_user, sender=ImagerProfile)
