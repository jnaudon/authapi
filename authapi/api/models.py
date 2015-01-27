from django.db import models
from django.contrib.auth.models import User

from jsonfield import JSONField

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import Q
from django.conf import settings
from utils import genhmac


CENSUS = (
    ('close', 'Close census'),
    ('open', 'Open census'),
)

AE_STATUSES = (
    ('notstarted', 'not-started'),
    ('started', 'started'),
    ('stopped', 'stopped'),
)

class AuthEvent(models.Model):
    auth_method = models.CharField(max_length=255)
    census = models.CharField(max_length=5, choices=CENSUS, default="close")
    auth_method_config = JSONField()
    extra_fields = JSONField()
    status = models.CharField(max_length=15, choices=AE_STATUSES, default="notstarted")

    def serialize(self):
        d = self.serialize_restrict()
        d.update({
            'auth_method_config': self.auth_method_config,
        })
        return d

    def serialize_restrict(self):
        d = {
            'id': self.id,
            'auth_method': self.auth_method,
            'census': self.census,
            'extra_fields': self.extra_fields,
            'users': self.userdata.count(),
        }
        return d

    def __str__(self):
        return "%s - %s" % (self.id, self.census)


STATUSES = (
    ('act', 'Active'),
    ('pen', 'Pending'),
    ('dis', 'Disabled'),
)

class UserData(models.Model):
    user = models.OneToOneField(User, related_name="userdata")
    event = models.ForeignKey(AuthEvent, related_name="userdata", null=True)
    tlf = models.CharField(max_length=20, null=True)
    credits = models.FloatField(default=0)
    metadata = JSONField(default="{}")
    status = models.CharField(max_length=255, choices=STATUSES, default="act")

    def get_perms(self, obj, permission, object_id=0):
        q = Q(object_type=obj, perm=permission)
        q2 = Q(object_id=object_id)
        if not object_id:
            q2 |= Q(object_id='')

        return self.acls.filter(q & q2)

    def has_perms(self, obj, permission, object_id=0):
        return bool(self.get_perms(obj, permission, object_id).count())

    def serialize(self):
        d = {
            'username': self.user.username,
            'credits': self.credits,
        }
        if self.user.email:
            d['email'] = self.user.email
        if self.tlf:
            d['tlf'] = self.tlf
        return d

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_data(sender, instance, created, *args, **kwargs):
    ud, _ = UserData.objects.get_or_create(user=instance)
    ud.save()


class ACL(models.Model):
    user = models.ForeignKey(UserData, related_name="acls")
    perm = models.CharField(max_length=255)
    object_type = models.CharField(max_length=255, null=True)
    object_id = models.CharField(max_length=255, default=0)

    def serialize(self):
        d = {
            'perm': self.perm,
            'object_type': self.object_type or '',
            'object_id': self.object_id or '',
        }
        return d

    def get_hmac(self):
        msg = ':'.join((self.user.user.username, self.object_type, str(self.object_id), self.perm))
        khmac = genhmac(settings.SHARED_SECRET, msg)
        return khmac

    def __str__(self):
        return "%s - %s - %s - %s" % (self.user.user.username, self.perm,
                                      self.object_type, self.object_id)


ACTIONS = (
    ('add', 'add_credits'),
    ('spend', 'spend_credits'),
)

STATUSES_CREDITS = (
    ('created', 'created'),
    ('done', 'done'),
    ('cancelled', 'cancelled'),
)

class CreditsAction(models.Model):
    user = models.ForeignKey(UserData, related_name="creditsactions")
    action = models.CharField(max_length=5, choices=ACTIONS, default="add")
    status = models.CharField(max_length=10, choices=STATUSES_CREDITS,
            default="created")
    quantity = models.FloatField()
    authevent = models.ForeignKey(AuthEvent, related_name="creditsactions", null=True)
    payment_metadata = JSONField(default="{}")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    #def serialize(self):
    #    d = {
    #        'id': self.id,
    #        'user': self.user.serialize(),
    #        'quantity': self.quantity,
    #        'action': self.action,
    #        'status': self.status,
    #        'created': self.created.isoformat(),
    #        'updated': self.updated.isoformat(),
    #    }
    #    return d

    def __str__(self):
        return self.name
