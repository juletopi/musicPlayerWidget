# Configuracao

Este projeto suporta dois servicos de musica: **Spotify** e **Last.fm**.
Voce so precisa configurar **um** deles.

- Se **ambos** estiverem configurados, o Spotify tem prioridade.
- Se apenas o **Spotify** estiver configurado, ele sera usado.
- Se apenas o **Last.fm** estiver configurado, ele sera usado.

## Inicio Rapido (desenvolvimento local)

1. Copie `.env.example` para `.env` e preencha suas credenciais de pelo menos um servico:

   ```bash
   cp .env.example .env
   ```

2. Rode:

   ```bash
   python start.py
   ```

Pronto. O launcher cria o ambiente virtual, instala dependencias, inicia o servidor Flask e abre o preview em `http://127.0.0.1:5000/preview`.

Pressione **Ctrl+C** para parar. Use `--no-open` para nao abrir o navegador automaticamente.

---

## Opcao 1: API do Spotify (recomendado)

### Criar app no Spotify Developer

- Crie uma aplicacao em [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
- Guarde:
  - `Client ID`
  - `Client Secret`
- Clique em **Edit Settings**
- Em **Redirect URIs**, adicione:
  - `https://example.com/callback`

## Refresh Token

### Script (recomendado)

So precisa de Python 3.9+, sem pacotes extras:

```bash
python scripts/get_token.py --lang pt-BR
```

O script:

1. Pede o `Client ID` e o `Client Secret` (ou le `SPOTIFY_CLIENT_ID` / `SPOTIFY_SECRET_ID` do ambiente)
2. Abre a pagina de autorizacao do Spotify no navegador
3. Pede para colar a **URL completa** para onde voce foi redirecionado (`https://example.com/callback?code=...`). A pagina em si nao carrega; isso e esperado
4. Imprime as duas linhas para configurar na Vercel:

```text
SPOTIFY_REFRESH_TOKEN=AQ...
SPOTIFY_REFRESH_TOKEN_DATE=2026-10-29
```

> [!IMPORTANT]
> **Codigo de autorizacao ≠ refresh token.** O valor `code=` da URL do callback so pode ser usado uma vez e expira em minutos; ele serve apenas para ser trocado pelo refresh token. Nunca coloque o codigo em `SPOTIFY_REFRESH_TOKEN`.

### Metodo manual

1. Acesse a URL abaixo substituindo `{SPOTIFY_CLIENT_ID}`:

```text
https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope=user-read-currently-playing,user-read-recently-played&redirect_uri=https://example.com/callback
```

2. Depois do login/autorizacao, copie o `{CODE}` da URL:

```text
https://example.com/callback?code={CODE}
```

3. Monte a string `{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}` e converta para Base64.

4. Execute:

```sh
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Basic {BASE64}" -d "grant_type=authorization_code&redirect_uri=https://example.com/callback&code={CODE}" https://accounts.spotify.com/api/token
```

> No Windows PowerShell, digite `curl.exe` em vez de `curl`: o `curl` puro e um alias de `Invoke-WebRequest` e falha com essas opcoes.

5. Salve o campo `refresh_token` da resposta JSON (nao o `access_token`, que dura uma hora) e a data de hoje como `SPOTIFY_REFRESH_TOKEN_DATE`.

## Expiracao do token

Desde 20 de julho de 2026, os refresh tokens do Spotify **expiram 6 meses depois que voce autoriza o app**, e usa-los nao renova esse prazo ([anuncio](https://developer.spotify.com/blog/2026-06-18-refresh-token-expiration)). Depois disso, o widget mostra o card *Token do Spotify expirou* (veja [Cards de erro](#cards-de-erro)).

Alem disso, apps em Development Mode so funcionam enquanto o dono do app tiver **Spotify Premium ativo**.

Para renovar:

1. Rode `python scripts/get_token.py --lang pt-BR`
2. Na Vercel, atualize `SPOTIFY_REFRESH_TOKEN` e `SPOTIFY_REFRESH_TOKEN_DATE` com os valores impressos
3. Faca o redeploy do projeto (Deployments → ⋯ → Redeploy) para os novos valores valerem

`SPOTIFY_REFRESH_TOKEN_DATE` e opcional, mas com ela o `/health/auth` informa quantos dias faltam (veja [Endpoints de Health Check](#endpoints-de-health-check)).

---

## Opcao 2: API do Last.fm

Last.fm e uma alternativa mais simples e sem OAuth. So precisa de API key e username.

### Obter API Key do Last.fm

1. Acesse [Last.fm API Account Creation](https://www.last.fm/api/account/create)
2. Preencha:
   - **Application name**: qualquer nome (ex.: "Now Playing Widget")
   - **Application description**: descricao curta
   - **Application homepage**: seu GitHub ou URL do repo
   - **Callback URL**: pode deixar vazio (nao e usado neste projeto)
3. Clique em **Submit**
4. Guarde o:
   - `API Key` (vira `LAST_FM_API_KEY`)

### Obter username do Last.fm

Voce encontra no perfil:
`https://www.last.fm/user/{SEU_USERNAME}`

Variavel:
- `LAST_FM_USERNAME`

### Variaveis de ambiente Last.fm

- `LAST_FM_API_KEY`
- `LAST_FM_USERNAME`

---

## Deploy

### Deploy na Vercel

- Crie conta em [Vercel](https://vercel.com/)
- Faca fork deste repositorio e conecte o projeto na Vercel
- Configure variaveis de ambiente em:
  - `https://vercel.com/<SeuNome>/<Projeto>/settings/environment-variables`

**Para Spotify:**
- `SPOTIFY_REFRESH_TOKEN`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_SECRET_ID`
- `SPOTIFY_REFRESH_TOKEN_DATE` (opcional, habilita a contagem de dias no `/health/auth`)

**Para Last.fm:**
- `LAST_FM_API_KEY`
- `LAST_FM_USERNAME`

- Deploy.

### Deploy no Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https%3A%2F%2Fgithub.com%2Fnovatorem%2Fnovatorem)

- Crie um app no Heroku (CLI ou Dashboard)
- Conecte ao repositorio e habilite automatic builds
- Depois do build, execute uma vez:
  - `heroku ps:scale web=1`

### Rodar local com Docker (alternativa)

```bash
docker compose up
```

Abra `http://localhost:5000/preview`.
Para parar:

```bash
docker compose down
```

---

## Trechos para README

**Spotify:**

`[![Spotify](https://music-player-widget-ten.vercel.app/api/spotify/)](https://open.spotify.com/user/USER_NAME)`

**Last.fm:**

`[![Last.fm](https://music-player-widget-ten.vercel.app/api/spotify/)](https://www.last.fm/user/USER_NAME)`

---

## Customizacao

### Parametros de URL

| Parametro | Descricao | Padrao | Exemplo |
|-----------|-----------|--------|---------|
| `background_color` | Cor de fundo do card (hex sem `#`) | `181414` | `0d1117` |
| `border_color` | Cor da borda (hex sem `#`) | `181414` | `ffffff` |
| `background_type` | Estilo de fundo: `color`, `blur_dark`, `blur_light` | `color` | `blur_dark` |
| `show_status` | Mostra "Vibing to:" ou "Recently played:" | `false` | `true` |
| `lang` | Idioma dos [cards de erro](#cards-de-erro): `en` ou `pt-BR` | `en` | `pt-BR` |

#### Tipos de fundo

- `color`: cor solida (padrao)
- `blur_dark`: capa desfocada com overlay escuro
- `blur_light`: capa desfocada com overlay claro

#### Exemplos

Basico:

```text
https://music-player-widget-ten.vercel.app/api/spotify/
```

Cores customizadas:

```text
https://music-player-widget-ten.vercel.app/api/spotify/?background_color=0d1117&border_color=30363d
```

Blur dark:

```text
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_dark
```

Blur light:

```text
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_light
```

Com status:

```text
https://music-player-widget-ten.vercel.app/api/spotify/?show_status=true
```

Tudo junto:

```text
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_dark&border_color=333333&show_status=true
```

### Templates de tema

Altere o `current-theme` em `api/templates.json`:

```json
{
  "current-theme": "dark",
  "templates": {
    "light": "spotify.html.j2",
    "dark": "spotify-dark.html.j2",
    "base": "base.html.j2"
  }
}
```

Temas disponiveis:
- `light`: fundo transparente, sem borda
- `dark`: fundo e borda customizaveis

### Criar tema customizado

1. Crie um template em `api/templates/` estendendo `base.html.j2`:

```jinja2
{% extends "base.html.j2" %}

{% block container_styles %}
/* Seus estilos */
background-color: var(--background-color);
border: 2px solid var(--border-color);
{% endblock %}

{% block theme_styles %}
/* Seus overrides */
.song {
  font-weight: 700;
}
{% endblock %}
```

2. Registre no `templates.json`:

```json
{
  "current-theme": "my-theme",
  "templates": {
    "light": "spotify.html.j2",
    "dark": "spotify-dark.html.j2",
    "my-theme": "my-theme.html.j2"
  }
}
```

### Endpoints de Health Check

**`/health`**: verifica se o servidor esta no ar. Responde `OK` (usado pelo healthcheck do Docker).

```text
https://music-player-widget-ten.vercel.app/api/spotify/health
```

**`/health/auth`**: faz uma autenticacao real com o servico configurado e responde em JSON. Status `200` quando a auth funciona, `503` quando falha ou quando nada esta configurado. O resultado fica em cache por 5 minutos.

```text
https://music-player-widget-ten.vercel.app/api/spotify/health/auth
```

```json
{"service": "spotify", "status": "ok", "token_date": "2026-10-29", "expires_on": "2027-04-29", "days_remaining": 182}
```

| Campo | Significado |
|-------|-------------|
| `service` | `spotify`, `lastfm` ou `null` |
| `status` | `ok` ou `error` |
| `error` | So em caso de falha: o mesmo codigo do [card de erro](#erros-comuns) |
| `token_date` / `expires_on` / `days_remaining` | Calculados a partir de `SPOTIFY_REFRESH_TOKEN_DATE`; `null` quando ela nao esta definida (e sempre no Last.fm) |
| `warning` | `invalid_token_date` quando `SPOTIFY_REFRESH_TOKEN_DATE` nao esta no formato `AAAA-MM-DD` |

Para ser avisado antes do token expirar, aponte qualquer job agendado para ele (cron, GitHub Actions no repo do seu perfil, um monitor de uptime). Por exemplo, este comando falha quando a auth esta quebrada ou faltam menos de 30 dias:

```bash
curl -fsS https://<seu-deploy>/api/spotify/health/auth | jq -e '.days_remaining == null or .days_remaining > 30'
```

### Animacoes reativas ao audio

**Spotify:**
- Barras no BPM real da musica
- Intensidade baseada em `energy`
- Curva da animacao ajustada por `danceability`

**Last.fm:**
- Se Spotify tambem estiver configurado, busca audio features no Spotify
- Caso contrario, usa padroes seguros (120 BPM, energia media)

---

## Cards de erro

Quando algo esta errado na configuracao, o widget nao vira uma imagem quebrada no seu README. Ele mostra um card no proprio visual do widget dizendo o que aconteceu e o que fazer, no idioma definido por `?lang=` (`en` ou `pt-BR`), com as suas cores e tamanho:

![Token do Spotify expirou](https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=token_expired&lang=pt-BR)

```text
https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=token_expired&lang=pt-BR
```

![Widget não configurado](https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=not_configured&lang=pt-BR&compact=true)

```text
https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=not_configured&lang=pt-BR&compact=true
```

`/preview/error?code=<codigo>` desenha qualquer card da tabela abaixo no seu proprio deploy, sem chamar o Spotify, para voce ver como cada um fica com os seus parametros.

Para diagnosticar a configuracao:

1. Abra a URL do widget no navegador e leia o card
2. Ou confira o header `X-Widget-Error` da resposta: `curl -sI "https://<seu-deploy>/api/spotify/" | grep -i x-widget-error`
3. Abra o `/health/auth` (veja [Endpoints de Health Check](#endpoints-de-health-check))
4. Procure o codigo abaixo

### Erros comuns

| Card (`X-Widget-Error`) | Causa | Solucao |
|-------------------------|-------|---------|
| Widget não configurado (`not_configured`) | Nenhuma variavel `SPOTIFY_*` ou `LAST_FM_*` | Configure as variaveis na Vercel e faca o redeploy |
| Token do Spotify expirou (`token_expired`) | Refresh token com mais de 6 meses, ou revogado | [Renove](#expiracao-do-token) com `scripts/get_token.py` |
| Credenciais do Spotify inválidas (`invalid_client`) | `SPOTIFY_CLIENT_ID` ou `SPOTIFY_SECRET_ID` errados | Copie de novo do dashboard do Spotify (cuidado com espacos sobrando) |
| Falha na autenticação do Spotify (`auth_failed`) | O Spotify recusou o pedido de token por outro motivo | Veja a linha `[spotify] token refresh failed` nos logs da Vercel |
| Acesso negado pelo Spotify (`premium_required`) | App em Development Mode cujo dono esta sem Premium ativo, ou sua conta fora da lista de usuarios do app | Renove o Premium na conta dona do app; adicione sua conta em **User Management** no dashboard |
| Serviço de música indisponível (`service_unavailable`) | Spotify ou Last.fm fora do ar ou inacessivel | Nada a corrigir do seu lado; volta sozinho |
| Erro no serviço de música (`api_error`) | Resposta inesperada da API | Veja os logs da Vercel |
| Nenhuma música para mostrar agora (`no_tracks`) | Esta tocando um podcast ou outro conteudo que nao e musica, e nao ha musica recente | Toque uma musica; o widget atualiza no proximo carregamento |
| Algo deu errado (`unknown`) | Erro inesperado | Veja os logs da Vercel; abra uma issue se continuar |

---

## Debug

Se tiver problema no setup, veja:
[Guia em video](https://youtu.be/n6d4KHSKqGk?t=615)

Se ainda falhar, verifique logs de funcoes da Vercel:
`https://vercel.com/{nome}/{projeto}/functions`

Na maioria dos casos, o erro e variavel de ambiente incorreta.

Os detalhes dos erros tambem aparecem nesses logs: uma falha ao renovar o token registra `[spotify] token refresh failed: HTTP <status> <resposta do Spotify>`.

**Rodando localmente atras de um proxy corporativo?** Se as requisicoes falharem com erro de certificado SSL, aponte o Python para o pacote de certificados da empresa:

```bash
export REQUESTS_CA_BUNDLE=/caminho/para/ca-da-empresa.pem   # PowerShell: $env:REQUESTS_CA_BUNDLE = "C:\caminho\para\ca-da-empresa.pem"
```
