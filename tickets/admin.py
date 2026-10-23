from django.contrib import admin

from .models import Reply, Ticket


class ReplyInline(admin.TabularInline):
    model = Reply
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "status", "priority", "category", "created_at")
    list_filter = ("status", "priority", "category", "company")
    search_fields = ("title", "description")
    inlines = [ReplyInline]
