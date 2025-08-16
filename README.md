# app-treemap

Este projeto Django exibe um gráfico Treemap de criptomoedas, permitindo que você analise o mercado e salve suas análises para futuras referências.
 
## API do CoinMarketCap

Este projeto utiliza a [API do CoinMarketCap](https://coinmarketcap.com/api/pricing/) para obter dados detalhados sobre criptomoedas. A API oferece uma ampla gama de informações atualizadas sobre diversas moedas.

Para mais detalhes sobre a API, consulte a [documentação oficial](https://coinmarketcap.com/api/documentation/v1/).

## Como usar

1. Clone o repositório

2. Crie e ative um ambiente virtual

3. Instale as dependências: pip install -r requirements.txt

4. Aplique as migrações: python manage.py migrate

5. Adicione sua API do CoinMarketCap -> chart/views.py -> "API_KEY = " 

6. Inicie o servidor: python manage.py runserver

7. Acesse no navegador: http://127.0.0.1:8000/
