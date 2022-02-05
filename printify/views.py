import json
from django.shortcuts import render
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django import forms


class CreateProductValidation(forms.Form):
    chartBase64 = forms.CharField()
    colour = forms.CharField()
    market = forms.CharField()
    sizes = forms.JSONField()
    symbol = forms.CharField()

@csrf_exempt
def create_product(request):
    """creates printify product"""

    #create image
    #replace hard data with variables
    #public product / port laravel logic

    if request.method == 'POST':
        form = CreateProductValidation(request.POST)
        if form.is_valid():

            #all the logic    

            return HttpResponse(status=200)
        else:
            return HttpResponse('Unprocessable Entity', status=422)        
    else:
        return HttpResponse('Method Not Allowed', status=405)


    url = "https://api.printify.com/v1/shops/4059401/products.json"

    payload = json.dumps({
        "title": "ADA #55",
        "description": "Stock Tee",
        "blueprint_id": 6,
        "print_provider_id": 61,
        "variants": [
            {
                "id": 12102,
                "sku": "85393203832296141203",
                "price": 900,
                "is_enabled": True
            },
            {
                "id": 12101,
                "sku": "30967999484636289818",
                "price": 900,
                "is_enabled": True
            },
            {
                "id": 12100,
                "sku": "26113178150344651753",
                "price": 900,
                "is_enabled": True
            }
        ],
        "print_areas": [
            {
                "variant_ids": [
                    12102,
                    12101,
                    12100
                ],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": "61fea524ddc250000193afc8",
                                "name": "",
                                "x": 0.5,
                                "y": 0.3,
                                "scale": 1,
                                "angle": 0
                            }
                        ]
                    }
                ]
            }
        ],
        "print_details": []
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjdhYTgwNWYwNDUxMDRkZjUzNThkZmIxMDQzNjhmMjFlY2UyYmE2YjVlYjIxNzM5ZTI3Yjc5MjczMzRjNzcxMmRiMWUxOGViNzc4M2I2YWNkIiwiaWF0IjoxNjQyNjkxOTgxLCJuYmYiOjE2NDI2OTE5ODEsImV4cCI6MTY3NDIyNzk4MSwic3ViIjoiOTI0ODMyOSIsInNjb3BlcyI6WyJzaG9wcy5tYW5hZ2UiLCJzaG9wcy5yZWFkIiwiY2F0YWxvZy5yZWFkIiwib3JkZXJzLnJlYWQiLCJvcmRlcnMud3JpdGUiLCJwcm9kdWN0cy5yZWFkIiwicHJvZHVjdHMud3JpdGUiLCJ3ZWJob29rcy5yZWFkIiwid2ViaG9va3Mud3JpdGUiLCJ1cGxvYWRzLnJlYWQiLCJ1cGxvYWRzLndyaXRlIiwicHJpbnRfcHJvdmlkZXJzLnJlYWQiXX0.AWd1tfE9o4ozYUATCJrFd5HqqOrnpVuDOvFettvk8iN_4CkdUPNgYb8Zqv-2kWqeVfIWtQPOSNDbHcxkYxg'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return HttpResponse(response.text)
