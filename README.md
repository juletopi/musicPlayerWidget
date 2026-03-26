<div align="center">
  <h2 align="center">Music Player Widget</h2>
</div>

<div align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python-badge" style="max-width: 100%;">
  </a>
  <a href="https://flask.palletsprojects.com/">
    <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask-badge" style="max-width: 100%;">
  </a>
  <a href="https://developer.spotify.com/">
    <img src="https://img.shields.io/badge/Spotify_API-1DB954?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify-badge" style="max-width: 100%;">
  </a>
  <a href="https://vercel.com/">
    <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel-badge" style="max-width: 100%;">
  </a>
</div>

<br>

<div align="center">
  <a href="#previews">Previews</a> &#xa0; • &#xa0;
  <a href="#setup">Setup</a> &#xa0; • &#xa0;
  <a href="#licença">Licença</a>
</div>

----

## Previews

| Variante | Widget |
|----------|--------|
| **Padrão** | [![Default](https://spotify-api-readme-fork.vercel.app/api/spotify/)](https://spotify-api-readme-fork.vercel.app/api/spotify/) |
| **Dark custom** | [![Dark Custom](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_color=0e1118&border_color=22252c)](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_color=0e1118&border_color=22252c) |
| **Blur dark** | [![Blur Dark](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_type=blur_dark&border_color=ffffff)](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_type=blur_dark&border_color=ffffff) |
| **Blur light** | [![Blur Light](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_type=blur_light&border_color=000000)](https://spotify-api-readme-fork.vercel.app/api/spotify/?background_type=blur_light&border_color=000000) |
| **Compacto** | [![Compact](https://spotify-api-readme-fork.vercel.app/api/spotify/?compact=true&background_type=blur_dark&border_color=ffffff)](https://spotify-api-readme-fork.vercel.app/api/spotify/?compact=true&background_type=blur_dark&border_color=ffffff) |
| **Com status** | [![Status On](https://spotify-api-readme-fork.vercel.app/api/spotify/?show_status=true&background_color=0e1118&border_color=22252c)](https://spotify-api-readme-fork.vercel.app/api/spotify/?show_status=true&background_color=0e1118&border_color=22252c) |

<div align="left">
  <h6><a href="#music-player-widget"> Voltar para o início ↺</a></h6>
</div>

## Setup

> [!IMPORTANT]
> Certifique-se de ter os seguintes requisitos antes de iniciar:
>
> <a href="https://www.python.org/">
>   <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python-badge">
> </a>
> <a href="https://developer.spotify.com/dashboard">
>   <img src="https://img.shields.io/badge/Spotify_App-1DB954?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify-badge">
> </a>

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/spotify-now-playing-widget.git
cd spotify-now-playing-widget
```

2. Copie o arquivo de ambiente
```bash
cp .env.example .env
```

3. Preencha as credenciais no `.env`
```
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_SECRET_ID=seu_client_secret
SPOTIFY_REFRESH_TOKEN=seu_refresh_token
```

> [!NOTE]
> Consulte o [SetUp.pt.md](SetUp.pt.md) para o passo a passo completo de como obter o `refresh_token` da API do Spotify.

4. Inicie o servidor local
```bash
python start.py
```

O launcher cria o ambiente virtual, instala dependências e abre o preview em `http://127.0.0.1:5000/preview`.

> [!TIP]
> Use `python start.py --no-open` para iniciar sem abrir o navegador automaticamente.

#### Leia a documentação de setup em outros idiomas:

<table>
  <tr>
    <th align="center">Idioma</th>
    <th align="center">Link</th>
  </tr>
  <tr>
    <td>
      <img align="center" src="https://cdn-icons-png.flaticon.com/512/197/197386.png" alt="Português" width="22"/>
      Português (Brasil)
    </td>
    <td align="center">
      <a href="SetUp.pt.md">SetUp.pt.md</a>
    </td>
  </tr>
  <tr>
    <td>
      <img align="center" src="https://cdn-icons-png.flaticon.com/512/197/197374.png" alt="English" width="22"/>
      English
    </td>
    <td align="center">
      <a href="SetUp.md">SetUp.md</a>
    </td>
  </tr>
</table>
<div align="left">
  <h6><a href="#music-player-widget"> Voltar para o início ↺</a></h6>
</div>

## Licença

Este projeto é baseado no do [novatorem/novatorem](https://github.com/novatorem/novatorem) e está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

<div align="left">
  <h6><a href="#music-player-widget"> Voltar para o início ↺</a></h6>
</div>

<br>

----

<div align="center">
  Feito com ❤️ e ☕ por <a href="https://github.com/juletopi">Juletopi</a>.
</div>
