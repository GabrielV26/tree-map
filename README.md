# App Tree Map

Aplicação Django que exibe um treemap das principais criptomoedas com dados da API do CoinMarketCap e permite salvar anotações autenticadas.

## Requisitos
- Python 3.10+
- Uma chave de API do CoinMarketCap

## Configuração local

1. Clone o repositório e entre na pasta do projeto.
2. Crie e ative um ambiente virtual.
3. Instale as dependências:

   `pip install -r requirements.txt`

4. Configure as variáveis de ambiente **fora do código-fonte**.

Linux/macOS:
```bash
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_DEBUG="True"
export DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost"
export COINMARKETCAP_API_KEY="sua-chave-aqui"
```

PowerShell:
```powershell
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(50))"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "127.0.0.1,localhost"
$env:COINMARKETCAP_API_KEY = "sua-chave-aqui"
```

5. Aplique as migrações e crie um usuário para acessar a área administrativa:

   `python manage.py migrate`
   
   `python manage.py createsuperuser`

6. Inicie o servidor:

   `python manage.py runserver`

7. Acesse `http://127.0.0.1:8000/`. Para salvar ou remover anotações, entre em `/login/`. O login comum é separado do painel administrativo `/admin/`.

## Configuração de produção

- Defina uma `DJANGO_SECRET_KEY` nova, forte e exclusiva, e configure `DJANGO_DEBUG=False`.
- Defina `DJANGO_ALLOWED_HOSTS` com os domínios reais separados por vírgula.
- Configure HTTPS no servidor e, quando apropriado, defina `DJANGO_SECURE_SSL_REDIRECT=True`, `DJANGO_SESSION_COOKIE_SECURE=True` e `DJANGO_CSRF_COOKIE_SECURE=True`.
- Defina `COINMARKETCAP_API_KEY` no ambiente de execução. Nunca comite chaves em arquivos Python, HTML ou no Git.
- Use `python manage.py check --deploy` antes da publicação.
- Rotacione qualquer chave que já tenha sido publicada. Apagar a chave do arquivo atual não a remove do histórico de commits.

## Segurança e testes

- A criação e remoção de anotações exigem login e POST com proteção CSRF.
- O parâmetro `limit` é validado e limitado a 1–100.
- A chamada externa tem timeout e respostas de erro não revelam detalhes internos.
- Texto fornecido pelo usuário é inserido no DOM como texto, não como HTML.
- Execute os testes com `python manage.py test`.

