from django.shortcuts import render
print("🔥 recognition/views.py đang được load bởi Django")

# Create your views here.
import io
import base64
import numpy as np
import cv2
from PIL import Image
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import os
import time
from .models import Feedback
import traceback
from ai_engine.camera_service import (
    start_camera,
    stop_camera,
    get_latest_frame_base64,
    get_latest_canvas_base64,
    clear_canvas
)
from ai_engine.preprocess import preprocess, define_transform
from ai_engine.cnn_model import get_model, inference


@api_view(["POST"])
def recognize_drawing(request):
    try:
        data = request.data.get("image")
        if not data:
            print("There is no image data in request.data")
            return Response({"error": "No image data uploaded"}, status=400)
        # --- Decode ảnh base64 ---
        try:
            header, encoded = data.split(",", 1)
            image_data = base64.b64decode(encoded)
        except Exception as e:
            print("Lỗi khi giải mã base64:", e)
            return Response({"error": "Incorrect image format"}, status=400)

        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        canvas_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        rgb = preprocess(canvas_bgr)
        trans = define_transform()
        tensor = trans(rgb)
        if tensor is None:
            print("Tensor None")
            return Response({"error": "No valid drawings detected"}, status=400)
        model = get_model()
        start = time.time()
        label, conf = inference(model, tensor)
        end = time.time()
        inference_time = end - start
        return Response({
            "label": label,
            "confidence": round(conf * 100, 2),
            "inference_time": inference_time
        })
    except Exception as e:
        print("Error in recognize_drawing:", e)
        return Response({"error": f"Processing error: {e}"}, status=500)
    

@csrf_exempt
def save_feedback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            name = data.get("name", "").strip() or "Anonymous"
            
            # Chuyển về bool 
            is_correct_raw = data.get("is_correct", False)
            if isinstance(is_correct_raw, str):
                is_correct = is_correct_raw.lower() in ["true", "1", "yes"]
            else:
                is_correct = bool(is_correct_raw)

            draw_by = data.get("draw_by", None)
            if not draw_by:
                # Nếu frontend không gửi, suy ra theo API gọi
                if "camera" in request.path.lower():
                    draw_by = "Camera"
                else:
                    draw_by = "Canvas"
                    
            inference_time = data.get("inference_time", None)
            fb = Feedback.objects.create(
                name=name,
                is_correct=is_correct,
                actual_label=data.get("actual_label", ""),
                image_data=data.get("image", ""),
                draw_by=draw_by,
                inference_time=inference_time,
            )

            print("Saved Feedback:", fb)
            return JsonResponse({"message": "Sent feedback successfully!"}, status=201)

        except Exception as e:
            print("Lỗi saving feedback", str(e))
            print(traceback.format_exc())  
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(["POST"])
def camera_start(request):
    start_camera()
    return Response({"message": "Camera started"})

# ⏹Stop
@api_view(["POST"])
def camera_stop(request):
    stop_camera()
    return Response({"message": "Camera stopped"})

# Clear
@api_view(["POST"])
def camera_clear(request):
    clear_canvas()
    return Response({"message": "Canvas cleared"})

# Get frame
@api_view(["GET"])
def camera_frame(request):
    frame_b64 = get_latest_frame_base64()
    return Response({"frame": frame_b64})

# Get canvas (ảnh trắng nét đen)
@api_view(["GET"])
def camera_canvas(request):
    canvas_b64 = get_latest_canvas_base64()
    return Response({"canvas": canvas_b64})