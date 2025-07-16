from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import identify_logic

@csrf_exempt  # for local dev / testing only
def identify_contact(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response_data = identify_logic(data)
            return JsonResponse(response_data, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

