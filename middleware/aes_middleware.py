import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from utils.aes_encryption import decrypt_aes, encrypt_aes

class AESMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.content_type == 'application/json' and request.body:
            try:
                raw_data = json.loads(request.body)
                if 'data' in raw_data:
                    decrypted = decrypt_aes(raw_data['data'])
                    request._body = decrypted.encode()
                    request.data = json.loads(decrypted)
            except Exception as e:
                return JsonResponse({'detail': f'Invalid encrypted data: {str(e)}'}, status=400)

    def process_response(self, request, response):
        try:
            if hasattr(response, 'data') and isinstance(response.data, dict):
                raw_json = json.dumps(response.data)
                encrypted = encrypt_aes(raw_json)
                return JsonResponse({'data': encrypted})
        except Exception:
            pass  # fall back to default if encryption fails
        return response
