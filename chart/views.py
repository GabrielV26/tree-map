import json
import os
import tempfile
from pathlib import Path

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .forms import SaveDetailForm
from .models import SaveDetail

DATA_FILE = Path(settings.BASE_DIR) / "crypto_data.json"
COINMARKETCAP_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
MAX_CRYPTO_LIMIT = 100
REQUEST_TIMEOUT_SECONDS = 10


def index(request):
    form = SaveDetailForm()
    data_form = SaveDetail.objects.filter(user=request.user).order_by("-created_at")[:8] if request.user.is_authenticated else []
    for detail in data_form:
        detail.formatted_created_at = (
            timezone.localtime(detail.created_at).strftime("%d/%m/%Y %H:%M:%S")
            if detail.created_at
            else None
        )
    return render(request, "index.html", {"form": form, "data_form": data_form})


def load_previous_data():
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_current_data(data):
    """Write the snapshot atomically to avoid leaving a partially written JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=DATA_FILE.parent, delete=False
        ) as file:
            json.dump(data, file)
            temp_name = file.name
        os.replace(temp_name, DATA_FILE)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def get_crypto_data(api_key, limit=10):
    params = {"start": "1", "limit": limit, "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": api_key}
    try:
        response = requests.get(
            COINMARKETCAP_URL,
            headers=headers,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        current_data = payload.get("data")
        if not isinstance(current_data, list):
            return None

        previous_data = load_previous_data()
        for crypto in current_data:
            symbol = crypto.get("symbol")
            quote = crypto.get("quote", {}).get("USD", {})
            if symbol and isinstance(quote, dict):
                crypto["previous_market_cap"] = previous_data.get(symbol, {}).get("market_cap")

        snapshot = {
            crypto["symbol"]: {"market_cap": crypto["quote"]["USD"]["market_cap"]}
            for crypto in current_data
            if crypto.get("symbol") and isinstance(crypto.get("quote", {}).get("USD"), dict)
            and "market_cap" in crypto["quote"]["USD"]
        }
        save_current_data(snapshot)
        return current_data
    except (requests.RequestException, ValueError, KeyError, TypeError, OSError):
        return None


@require_GET
def get_data(request):
    raw_limit = request.GET.get("limit", "10")
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return JsonResponse({"error": "O parâmetro limit deve ser um número inteiro."}, status=400)
    if not 1 <= limit <= MAX_CRYPTO_LIMIT:
        return JsonResponse(
            {"error": f"O parâmetro limit deve estar entre 1 e {MAX_CRYPTO_LIMIT}."},
            status=400,
        )

    api_key = os.environ.get("COINMARKETCAP_API_KEY", "").strip()
    if not api_key:
        return JsonResponse(
            {"error": "A API do CoinMarketCap não está configurada no servidor."},
            status=503,
        )

    crypto_data = get_crypto_data(api_key, limit)
    if crypto_data is None:
        return JsonResponse(
            {"error": "Não foi possível recuperar os dados do mercado. Tente novamente mais tarde."},
            status=502,
        )

    processed_data = []
    for crypto in crypto_data:
        try:
            quote = crypto["quote"]["USD"]
            processed_data.append({
                "name": str(crypto["name"]),
                "symbol": str(crypto["symbol"]),
                "market_cap": float(quote["market_cap"]),
                "previous_market_cap": (
                    float(crypto["previous_market_cap"])
                    if crypto.get("previous_market_cap") is not None
                    else None
                ),
            })
        except (KeyError, TypeError, ValueError):
            continue
    return JsonResponse({"treemap": processed_data})


@require_POST
def save_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Autenticação necessária."}, status=401)
    form = SaveDetailForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"status": "error", "message": form.errors.get_json_data()}, status=400)
    detail = form.save(commit=False)
    detail.user = request.user
    detail.save()
    return JsonResponse({"status": "success", "id": detail.id, "text": detail.text})


@require_POST
def delete_data(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Autenticação necessária."}, status=401)
    detail = get_object_or_404(SaveDetail, id=id, user=request.user)
    detail.delete()
    return JsonResponse({"status": "success", "message": "Análise removida."})
