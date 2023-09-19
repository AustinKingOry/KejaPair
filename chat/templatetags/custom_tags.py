from django import template
from django.template.defaultfilters import stringfilter
from KejaPair.settings import SECRET_KEY
from base.basicFunctions import createId,encrypt_text,decrypt_text

register = template.Library()

@register.filter
@stringfilter
def decrypt_message(cipher_text):
    key = b'*#*#@kejapair#*#'
    return decrypt_text(key,cipher_text)