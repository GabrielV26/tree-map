from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import SaveDetail
from .forms import SaveDetailForm
from django.utils import timezone
import requests
import json
import os


# Função para renderizar a página inicial
def index(request):
    form = SaveDetailForm()
    data_form = SaveDetail.objects.all().order_by('-created_at')[:8]

    for detail in data_form:
        if detail.created_at:
            detail.formatted_created_at = timezone.localtime(detail.created_at).strftime('%d/%m/%Y %H:%M:%S')
        else:
            detail.formatted_created_at = None

    return render(request, 'index.html', {'form': form, 'data_form': data_form})


# Chave da API do CoinMarketCap
API_KEY = '2767653c-9b83-4202-8d26-7c26afde4c8c'

DATA_FILE = 'crypto_data.json'


# Função para carregar dados anteriores salvos em um arquivo JSON
def load_previous_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}


# Função para salvar os dados atuais em um arquivo JSON
def save_current_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


# Função para buscar dados de criptomoedas da API CoinMarketCap
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
        current_data = response.json()['data']

        previous_data = load_previous_data()
        for crypto in current_data:
            symbol = crypto['symbol']
            crypto['previous_market_cap'] = previous_data.get(symbol, {}).get('market_cap', 0)

        # Salvar os dados atuais para comparação futura
        save_current_data({crypto['symbol']: {'market_cap': crypto['quote']['USD']['market_cap']} for crypto in current_data})

        return current_data
    else:
        return None


# Função para obter dados de criptomoedas e enviar como resposta JSON
def get_data(request):
    limit = request.GET.get('limit', 10)
    crypto_data = get_crypto_data(API_KEY, limit)

    if crypto_data is not None:
        processed_data = [
            {
                'name': crypto['name'],
                'symbol': crypto['symbol'],
                'market_cap': crypto['quote']['USD']['market_cap'],
                'previous_market_cap': crypto['previous_market_cap']
            }
            for crypto in crypto_data
        ]
        return JsonResponse({'treemap': processed_data})
    else:
        return JsonResponse({'treemap': 'Falha ao recuperar dados do Treemap'}, status=500)


# Função para salvar dados através do formulário e enviar resposta JSON
def save_data(request):
    if request.method == 'POST':
        form = SaveDetailForm(request.POST)
        if form.is_valid():
            form.save()
            data_chart_text = form.cleaned_data['text']
            return JsonResponse({'status': 'success', 'text': data_chart_text})
        else:
            return JsonResponse({'status': 'error', 'message': form.errors}, status=400)
    return HttpResponseBadRequest('Método de requisição ou tipo de conteúdo inválido')


# Função para deletar dados com base no ID e enviar resposta JSON
def delete_data(request, id):
    if request.method == 'POST':
        detail = get_object_or_404(SaveDetail, id=id)
        detail.delete()
        return JsonResponse({'status': 'success', 'message': 'Dados deletados com sucesso.'})
    return HttpResponseBadRequest('Método de requisição inválido')
