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

5. Salve o campo `refresh_token` da resposta JSON.

### Metodo PowerShell

<details>

<summary>Script PowerShell para obter o refresh token</summary>

```powershell
$ClientId = Read-Host "Client ID"
$ClientSecret = Read-Host "Client Secret"

Start-Process "https://accounts.spotify.com/authorize?client_id=$ClientId&response_type=code&scope=user-read-currently-playing,user-read-recently-played&redirect_uri=https://example.com/callback"

$Code = Read-Host "Please insert everything after 'https://example.com/callback?code='"

$ClientBytes = [System.Text.Encoding]::UTF8.GetBytes("${ClientId}:${ClientSecret}")
$EncodedClientInfo =[Convert]::ToBase64String($ClientBytes)

curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Basic $EncodedClientInfo" -d "grant_type=authorization_code&redirect_uri=https://example.com/callback&code=$Code" https://accounts.spotify.com/api/token
```

</details>

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

### Health Check

Endpoint:

```text
https://music-player-widget-ten.vercel.app/api/spotify//health
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

## Debug

Se tiver problema no setup, veja:
[Guia em video](https://youtu.be/n6d4KHSKqGk?t=615)

Se ainda falhar, verifique logs de funcoes da Vercel:
`https://vercel.com/{nome}/{projeto}/functions`

Na maioria dos casos, o erro e variavel de ambiente incorreta.
