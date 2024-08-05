from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from .models import SaveDetail
from .forms import SaveDetailForm
import requests
import json


def index(request):
    form = SaveDetailForm()
    return render(request, 'index.html', {'form': form})


# API free do CoinMarketCap
API_KEY = '2767653c-9b83-4202-8d26-7c26afde4c8c'


def get_crypto_data(api_key, limit=10):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    params = {
        'start': '1',
        'limit': str(limit),
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return None


def get_data(request):
    limit = request.GET.get('limit', 10)
    crypto_data = get_crypto_data(API_KEY, limit)

    if crypto_data is not None:
        processed_data = [
            {
                'name': crypto['name'],
                'symbol': crypto['symbol'],
                'market_cap': crypto['quote']['USD']['market_cap']
            }
            for crypto in crypto_data
        ]
        return JsonResponse({'treemap': processed_data})
    else:
        return JsonResponse({'treemap': 'Failed to retrieve Treemap data'}, status=500)


def save_data(request):
    if request.method == 'POST' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            data_chart_text = data.get('text', '')
            if data_chart_text:
                SaveDetail.objects.create(text=data_chart_text)
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No data text provided'}, status=400)
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON')
    elif request.method == 'POST':
        form = SaveDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': form.errors}, status=400)
    elif request.method == 'GET':
        form = SaveDetailForm()
        return render(request, 'index.html', {'form': form})
    return HttpResponseBadRequest('Invalid request method or content type')
