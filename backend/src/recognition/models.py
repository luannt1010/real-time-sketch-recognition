from django.db import models
import datetime

# Create your models here.
class Feedback(models.Model):
    name = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    actual_label = models.CharField(max_length=50, blank=True, null=True)
    image_data = models.TextField()  # base64 ảnh người vẽ
    draw_by = models.CharField(max_length=20, default="Canvas")  
    inference_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Correct" if self.is_correct else f"Wrong ({self.actual_label})"
        return f"{self.name} - {status} - {self.draw_by}"
