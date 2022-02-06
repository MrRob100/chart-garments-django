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
    # sizes = forms.JSONField()
    symbol = forms.CharField()

@csrf_exempt
def create_product(request):
    """creates printify product"""

    #publish product / port laravel logic

    if request.method == 'POST':
        form = CreateProductValidation(json.loads(request.body))

        if form.is_valid():

            body = json.loads(request.body)

            title = body['symbol'] + '#' + str(random.randint(0, 1000))
            # validBase64 = os.environ.get('BIGGER_IMAGE').replace('data:image/png;base64,', '')
            validBase64 = body['chartBase64'].replace('data:image/png;base64,', '')

            imagesUrl = "https://api.printify.com/v1/uploads/images.json"

            imagePayload = json.dumps({
                "file_name": title,
                "contents": validBase64
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + os.environ.get('PRINTIFY_TOKEN'),
            }

            imageResponse = requests.request("POST", imagesUrl, headers=headers, data=imagePayload)
            imageId = json.loads(imageResponse.text)['id']

            productUrl = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products.json"

            price = int(os.environ.get('TEE_PRICE'))

            productPayload = json.dumps({
                "title": title,
                "description": "Stock Tee",
                "blueprint_id": 6,
                "print_provider_id": 61,
                "variants": [
                    {
                        "id": 12102,
                        "sku": "85393203832296141203",
                        "price": price,
                        "is_enabled": True
                    },
                    {
                        "id": 12101,
                        "sku": "30967999484636289818",
                        "price": price,
                        "is_enabled": True
                    },
                    {
                        "id": 12100,
                        "sku": "26113178150344651753",
                        "price": price,
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
                                        "id": imageId,
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

            productResponse = requests.request("POST", productUrl, headers=headers, data=productPayload)
            #probably low quality image
            # return HttpResponse(response.text, status=200)

            productsUrl = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products.json"
            productsResponse = requests.request("GET", productsUrl, headers=headers)

            # return HttpResponse(publishResponse.text)
            # return HttpResponse(json.loads(publishResponse.text)['data'])

            # productId = 55555

            # publishUrl = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products/" + productId + "/publish.json"



            return HttpResponse(productResponse.text, status=200)
        else:
            return HttpResponse('Unprocessable Entity', status=422)        
    else:
        return HttpResponse('Method Not Allowed', status=405)
