from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import json
import functools
from .models import Captcha


def valid_capcha(request):
    if request.method == 'GET':
        code = request.GET.get('captcha_code', '')
        answer = request.GET.get('captcha_answer', '')
    else:
        req = json.loads(request.body.decode('utf-8'))
        code = req.get('captcha_code', '')
        answer = req.get('captcha_answer', '')

    try:
        captcha = Captcha.objects.get(code=code)
    except ObjectDoesNotExist:
        return False

    if not captcha.challenge.upper() == answer.upper():
        captcha.delete()
        return False
    captcha.delete()
    return True


class captcha_required(object):

    def __init__(self, func):
        self.func = func
        functools.wraps(self.func)(self)

    def __call__(self, request, *args, **kwargs):
        if not settings.ENABLE_CAPTCHA:
            return self.func(request, *args, **kwargs)

        if not valid_capcha(request):
            return HttpResponseForbidden('Invalid captcha')

        return self.func(request, *args, **kwargs)
