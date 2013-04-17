# -*- coding: utf-8 -*-
#

# Core imports
import requests

# 3rd party imports
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.sites.models import Site

# Project imports
from models import ExternalURL, URL, Release, DeploymentHost


# Global variables
VALID_CODES = [200, 301, 302]
CURRENT_SITE = Site.objects.get_current()


class ReleaseAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'timestamp', 'user', 'download', 'deploy',)
    list_filter = ('date_created', 'user',)
    ordering = ('-date_created',)
    exclude = ('user',)
    readonly_fields = ('user', 'timestamp', 'date_created', 'archive',)
    actions = ('delete_releases',)

    def has_add_permission(self, request):
        return False

    def download(self, instance):
        return u'<a href="%s%s" target="_blank">Download</a>' % (settings.STATIC_URL, instance.archive)
    download.short_description = u'Archiv'
    download.allow_tags = True

    def deploy(self, instance):
        return u'<a href="/admin/statify/release/%s/deploy/select/">Deploy</a>' % (instance.id)
    deploy.short_description = u'Staging'
    deploy.allow_tags = True

    def delete_releases(modeladmin, request, queryset):
        for release in queryset:
            release.delete()
        messages.success(request, 'Die ausgewählten Releases wurden erfolgreich gelöscht.')
    delete_releases.short_description = "Ausgewählte Releases löschen"

    # Remove default query delete
    def get_actions(self, request):
        actions = super(ReleaseAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

admin.site.register(Release, ReleaseAdmin)


class DeploymentHostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'path', 'user')
    list_filter = ('type',)
    fieldsets = (
        (None, {
            'fields': ('type', 'title', 'url',),
        }),
        (u'Server', {
            'fields': ('host', 'path',),
        }),
        (u'Authentifizierung', {
            'fields': ('authtype', 'user', 'password',),
            'classes': ('wide',)
        }),
    )

admin.site.register(DeploymentHost, DeploymentHostAdmin)


class URLForm(forms.ModelForm):
    class Meta:
        model = URL

    def clean(self):
        # Check if url is entered
        if not 'url' in self.cleaned_data or self.cleaned_data['url'] is '':
            raise forms.ValidationError(u'Das Feld URL muss ausgefüllt werden.')

        cleaned_url = self.cleaned_data['url']
        url = u'http://%s%s' % (CURRENT_SITE, cleaned_url)

        # Check if url is entered
        if len(URL.objects.filter(url=cleaned_url).exclude(pk=self.instance.pk)) > 0:
            raise forms.ValidationError('Die eingegebene URL existiert bereits.')

        # Check if url starts with a slash
        if not cleaned_url.startswith('/'):
            raise forms.ValidationError(u'Die eingegebene URL muss mit einem / beginnen.')

        request = requests.get(url)

        # Check if url exists and
        if request.status_code in VALID_CODES:
            return self.cleaned_data
        else:
            raise forms.ValidationError(u'Bitte geben Sie eine gültige URL ein. Die URL "%s" ist nicht erreichbar. Statuscode: %s' % (url, request.status_code))


def validate_urls(modeladmin, request, queryset):
    for u in queryset:
        url = u'http://%s%s' % (CURRENT_SITE, u)
        request = requests.get(url)

        if request.status_code in VALID_CODES:
            u.is_valid = True
        else:
            u.is_valid = False

        u.save()
validate_urls.short_description = u'Ausgewählte URLs überprüfen'


class URLAdmin(admin.ModelAdmin):
    exclude = ('is_valid',)
    list_display = ('url', 'is_valid', 'preview_url',)
    list_filter = ('is_valid',)
    actions = [validate_urls]
    form = URLForm
    ordering = ('url',)

    def preview_url(self, instance):
        return u'<a href="http://%s%s" target="_blank" rel="nofollow">Vorschau</a>' % (CURRENT_SITE, instance.url)
    preview_url.short_description = u''
    preview_url.allow_tags = True

admin.site.register(URL, URLAdmin)


def validate_external_urls(modeladmin, request, queryset):
    for u in queryset:
        request = requests.get(u.url)

        if request.status_code in VALID_CODES:
            u.is_valid = True
        else:
            u.is_valid = False

        u.save()
validate_external_urls.short_description = u'Ausgewählte External URLs überprüfen'


class ExternalURLForm(forms.ModelForm):
    class Meta:
        model = ExternalURL

    def clean(self):
        # Check if url is entered
        if not 'url' in self.cleaned_data or self.cleaned_data['url'] is '':
            raise forms.ValidationError(u'Das Feld URL muss ausgefüllt werden.')

        cleaned_url = self.cleaned_data['url']
        url = u'%s' % (cleaned_url)

        # Check if url already exists
        if len(URL.objects.filter(url=cleaned_url).exclude(pk=self.instance.pk)) > 0:
            raise forms.ValidationError('Die eingegebene URL existiert bereits.')

        request = requests.get(url)

        # Check if url exists and
        if request.status_code in VALID_CODES:
            return self.cleaned_data
        else:
            raise forms.ValidationError(u'Bitte geben Sie eine gültige URL ein. Die URL "%s" ist nicht erreichbar. Statuscode: %s' % (url, request.status_code))


class ExternalURLAdmin(admin.ModelAdmin):
    exclude = ('is_valid',)
    list_display = ('url', 'path', 'is_valid', 'preview_url',)
    list_filter = ('is_valid',)
    form = ExternalURLForm
    actions = [validate_external_urls]

    def preview_url(self, instance):
        return u'<a href="%s" target="_blank" rel="nofollow">Vorschau</a>' % (instance.url)
    preview_url.short_description = u''
    preview_url.allow_tags = True

admin.site.register(ExternalURL, ExternalURLAdmin)
