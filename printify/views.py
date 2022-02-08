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
            if imageResponse.status_code == 200:
                imageId = json.loads(imageResponse.text)['id']

                productUrl = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products.json"

                price = int(os.environ.get('TEE_PRICE'))

                ids = {
                    'sblack': {
                        'id': 12126,
                        'sku': '22214798185891630194'
                    },
                    'swhite': {
                        'id': 12102,
                        'sku': '12998278879033878343'
                    },
                    'mblack': {
                        'id': 12125,
                        'sku': '31844803643439321012'
                    },
                    'mwhite': {
                        'id': 12101,
                        'sku': '27722326231287582049'
                    },
                    'lblack': {
                        'id': 12124,
                        'sku': '63070809109122801291'
                    },
                    'lwhite': {
                        'id': 12100,
                        'sku': '39585749627759935185'
                    },
                    'xlblack': {
                        'id': 12127,
                        'sku': '64025329163857954691'
                    },
                    'xlwhite': {
                        'id': 12103,
                        'sku': '31301433701339422639'
                    },
                }

                productPayload = json.dumps({
                    "title": title,
                    "description": body['market'] + " Tee",
                    "blueprint_id": 6,
                        "print_provider_id": 61,
                        "variants": [
                            {
                                "id": ids['s' + body['colour']]['id'],
                                "sku": ids['s' + body['colour']]['sku'],
                                "price": price,
                                "is_enabled": True
                            },
                            {
                                "id": ids['m' + body['colour']]['id'],
                                "sku": ids['m' + body['colour']]['sku'],
                                "price": price,
                                "is_enabled": True
                            },
                            {
                                "id": ids['l' + body['colour']]['id'],
                                "sku": ids['l' + body['colour']]['sku'],
                                "price": price,
                                "is_enabled": True
                            },
                            {
                                "id": ids['xl' + body['colour']]['id'],
                                "sku": ids['xl' + body['colour']]['sku'],
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

                productResFormatted = json.loads(productResponse.text)

                if 'id' in productResFormatted:

                    publishPayload = json.dumps({
                        "title": True,
                        "description": True,
                        "images": True,
                        "variants": True,
                        "tags": True,
                    })

                    publishUrl = "https://api.printify.com/v1/shops/" + os.environ.get('PRINTIFY_STORE_ID') + "/products/" + productResFormatted['id'] + "/publish.json"
                    publishResponse = requests.request(
                        "POST", publishUrl, headers=headers, data=publishPayload)

                    if publishResponse.status_code == 200:
                        productResFormatted['sizes'] = body['sizes']

                        return HttpResponse(json.dumps(productResFormatted), status=publishResponse.status_code)
                    else:
                        return HttpResponse(publishResponse.text, status=publishResponse.status_code)
                else:
                    return HttpResponse(productResponse.text, status=productResponse.status_code)
            else:
                return HttpResponse(imageResponse, status=imageResponse.status_code)
        else:
            return HttpResponse('Unprocessable Entity', status=422)        
    else:
        return HttpResponse('Method Not Allowed', status=405)

def catalog(request):

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + os.environ.get('PRINTIFY_TOKEN'),
    }

    url = 'https://api.printify.com/v1/shops/' + os.environ.get('PRINTIFY_STORE_ID') + '/products.json'

    productResponse = requests.request("GET", url, headers=headers)

    return HttpResponse(productResponse.text, status=productResponse.status_code)
