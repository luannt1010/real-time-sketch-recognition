from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Feedback
from django.utils.html import format_html
import csv
from django.http import HttpResponse


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "is_correct", "actual_label", "draw_by", "preview_image", "inference_time", "created_at")
    list_filter = ("is_correct", "actual_label", "draw_by", "inference_time", "created_at")
    search_fields = ("name", "actual_label", "draw_by", "inference_time")

    def preview_image(self, obj):
        if obj.image_data:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:contain; border:1px solid #ccc;" />',
                obj.image_data
            )
        return "No image"
    preview_image.short_description = "Preview"

    actions = ["export_as_csv"]
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="feedback.csv"'
        writer = csv.writer(response)
        writer.writerow(["Name", "Is Correct", "Actual Label", "Draw By","Preview", "Inference Time", "Created At"])

        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.is_correct,
                obj.actual_label,
                obj.draw_by,
                obj.image_data or "",
                obj.inference_time,
                obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])
        return response

    export_as_csv.short_description = "Export selected feedback to CSV"
    