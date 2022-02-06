import json
import os
import random
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
            title = request.POST.get('symbol') + '#' + random.randint(0, 1000)
            validBase64 = request.POST.get('chartBase64').replace('data:image/png;base64,', '')

            imagesUrl = "https://api.printify.com/v1/uploads/images.json"

            payload = json.dumps({
                "file_name": title,
                "contents": validBase64
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + os.environ.get('PRINTIFY_TOKEN'),
            }

            imageResponse = requests.request("POST", imagesUrl, headers=headers, data=payload)

            url = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products.json"

            payload = json.dumps({
                "title": title,
                "description": "Stock Tee",
                "blueprint_id": 6,
                "print_provider_id": 61,
                "variants": [
                    {
                        "id": 12102,
                        "sku": "85393203832296141203",
                        "price": os.environ.get('TEE_PRICE'),
                        "is_enabled": True
                    },
                    {
                        "id": 12101,
                        "sku": "30967999484636289818",
                        "price": os.environ.get('TEE_PRICE'),
                        "is_enabled": True
                    },
                    {
                        "id": 12100,
                        "sku": "26113178150344651753",
                        "price": os.environ.get('TEE_PRICE'),
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
                                        "id": imageResponse.id,
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
                'Authorization': 'Bearer ' + os.environ.get('PRINTIFY_TOKEN'),
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            return HttpResponse(response.text, status=200)
        else:
            return HttpResponse('Unprocessable Entity', status=422)        
    else:
        return HttpResponse('Method Not Allowed', status=405)
