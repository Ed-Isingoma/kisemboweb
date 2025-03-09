from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.hashers import make_password
from .models import Account, Session, Topic, TopicVideo, Subscription

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_confirmed')
    list_filter = ('is_confirmed',)
    search_fields = ('email', 'name')
    fieldsets = (
        (None, {'fields': ('name', 'email', 'password', 'is_confirmed', 'code')}),
    )
    def save_model(self, request, obj, form, change):
        if change:
            original = Account.objects.get(pk=obj.pk)
            if original.password != obj.password:
                obj.password = make_password(obj.password)
        else:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('sessionID', 'userID', 'expiry')
    list_filter = ('expiry',)
    search_fields = ('userID__email',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('topicName', 'dailyPrice', 'weeklyPrice', 'monthlyPrice')
    list_filter = ('dailyPrice', 'weeklyPrice', 'monthlyPrice')
    search_fields = ('topicName',)

@admin.register(TopicVideo)
class TopicVideoAdmin(admin.ModelAdmin):
    list_display = ('videoName', 'topicID', 'videoLink', 'thumbnail_preview')
    search_fields = ('videoName',)
    readonly_fields = ('thumbnail_preview',)
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="data:image/png;base64,{}" style="max-height:50px;" />', obj.thumbnail)
        return "-"
    thumbnail_preview.short_description = "Thumbnail"

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('userID', 'topicID', 'expiry')
    list_filter = ('expiry',)
    search_fields = ('userID__email', 'topicID__topicName')
    list_editable = ('expiry',)
