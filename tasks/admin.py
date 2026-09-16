from django.contrib import admin

from .models import Comment, Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "type", "assignee", "author", "date", "status"]
    list_filter = ["type", "status", "date"]
    search_fields = ["title", "description"]
    date_hierarchy = "date"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["task", "author", "created_at"]
    search_fields = ["text"]
