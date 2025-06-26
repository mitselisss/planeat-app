from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from ..models import Feedback

@api_view(['POST'])
def feedback(request, user_id):
    # Check the request method.
    if request.method != "POST":
        return JsonResponse({'error': 'No POST request.'}, status=400)
    if User.objects.filter(id=user_id).exists():
        user = User.objects.get(id=user_id)
    else:
        return JsonResponse({'error': f"No User with User id:{user_id}"}, status=400)

    data = request.data  # Fetch the data from the frontend.

    content = data.get('feedback')
    if not content:
        return JsonResponse({'error': 'Content is required.'}, status=400)

    Feedback.objects.create(user=user, content=content)

    return JsonResponse({'message': 'Feedback saved'}, status=200)