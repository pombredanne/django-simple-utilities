# coding: utf-8
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from django.utils.encoding import force_unicode
from django.forms.widgets import Media

class FormsMixin(object):
    success_url = None
    forms_class = {}
    initials = {}
    messages_valid = {}
    messages_invalid = {}
    
    def get_valid_message(self, form, form_key):
        if self.messages_valid.get(form_key):
            return self.messages_valid.get(form_key)
        return self.messages_valid.get('default')
    
    def get_invalid_message(self, form, form_key):
        if self.messages_invalid.get(form_key):
            return self.messages_invalid.get(form_key)
        return self.messages_invalid.get('default')
    
    def form_invalid(self, form, form_key, message_text= None):
        message_text = message_text or self.get_invalid_message(form, form_key)
        if message_text:
            messages.error(
                self.request,
                force_unicode(message_text),
                extra_tags=form_key
            )
        return self.get(self.request)
    
    def form_valid(self, form, form_key, message_text = None):
        message_text = message_text or self.get_valid_message(form, form_key)
        if message_text:
            messages.success(
                self.request,
                force_unicode(message_text),
                extra_tags=form_key
            )
        return HttpResponseRedirect('')
    
    def get_success_url(self):
        return self.success_url or ''
    
    def get_context_data(self, **kwargs):
        context = super(FormsMixin, self).get_context_data(**kwargs)
        forms = self.get_forms()
        context['forms'] = forms
        context['media'] = self.get_media(forms)
        return context
    
    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if 'all' in self.request.POST:
            for key, val in forms.items():
                if (not val.is_valid()):
                    return self.form_invalid(forms, key)
            return self.form_valid(forms, key)
        
        
        for key, val in forms.items():
            if key in self.request.POST:
                if (val.is_valid()):
                    return self.form_valid(val, key)
                else:
                    return self.form_invalid(val, key)

    def get_form_messages(self, tag):
        form_messages =[]
        for message in messages.get_messages(self.request):
            if (message.extra_tags == tag):
                form_messages.append(message)
        return form_messages
        
    def get_form(self, form_class, form_key):
        form = form_class(**self.get_form_kwargs(form_key))
        form.messages = self.get_form_messages(form_key)
        form.form_key = form_key
        return form
    
    def get_form_kwargs(self, form_key):
        kwargs = {'initial': self.get_initial(form_key)}
        if self.request.method in ('POST', 'PUT') and (form_key in self.request.POST or 'all' in self.request.POST):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        
        instance = self.get_instance(form_key)
        if instance:
            kwargs['instance'] = instance
        return kwargs
    
    def get_initial(self, form_key):
        return self.initials.get(form_key)
     
    def get_instance(self, form_key):
        return None
           
    def get_forms(self):
        forms = {}
        for key, val in self.forms_class.items():
            forms[key] = self.get_form(val, key)
        return forms

    def get_media(self, forms):
        media = Media()
        for key, form in forms.items():
            media += form.media
        return media
        
        
        

class DetailFormsView(FormsMixin, DetailView):
    pass
    
    
    
class ListFormsView(FormsMixin, ListView):
    pass
    
    
class FormsView(FormsMixin, TemplateView):
    pass
    