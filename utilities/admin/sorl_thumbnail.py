from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings

from sorl.thumbnail.fields import ImageField
from sorl.thumbnail.shortcuts import get_thumbnail

class AdminImageWidget(forms.ClearableFileInput):
    """
    An ImageField Widget for django.contrib.admin that shows a thumbnailed
    image as well as a link to the current one if it hase one.
    """

    template_with_initial = u'%(clear_template)s<br />%(input_text)s: %(input)s'
    template_with_clear = u'%(clear)s <label style="width:auto" for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    def render(self, name, value, attrs=None):
        output = super(AdminImageWidget, self).render(name, value, attrs)
        if value and hasattr(value, 'url'):
            try:
                mini = get_thumbnail(value, 'x80', upscale=False)
            except Exception:
                pass
            else:
                output = (
                    u'<div style="float:left">'
                    u'<a style="width:%spx;display:block;margin:0 0 10px" class="image-link" href="%s">'
                    u'<img src="%s"></a>%s</div>'
                    ) % (mini.width, value.url, mini.url, output)
        return mark_safe(output)
    
    class Media:
        css = {
            'all': ('%sutilities/css/colorbox.css' % settings.STATIC_URL,)
        }
        js = (

                '%sutilities/js/jquery-1.6.4.min.js' % settings.STATIC_URL,
                '%sutilities/js/jquery.colorbox-min.js' % settings.STATIC_URL,
                '%sutilities/sorl/js/images-main.js' % settings.STATIC_URL,
              )


class AdminImageMixin(object):
    """
    This is a mix-in for InlineModelAdmin subclasses to make ``ImageField``
    show nicer form widget
    """
    def formfield_for_dbfield(self, db_field, **kwargs):
        if isinstance(db_field, ImageField):
            return db_field.formfield(widget=AdminImageWidget)
        sup = super(AdminImageMixin, self)
        return sup.formfield_for_dbfield(db_field, **kwargs)