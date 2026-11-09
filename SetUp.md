# Set Up

This project supports two music services: **Spotify** and **Last.fm**. You only need to configure one of them.

- If **both** are configured, Spotify takes priority.
- If only **Spotify** is configured, Spotify will be used.
- If only **Last.fm** is configured, Last.fm will be used.

## Quick Start (Local Development)

1. Copy `.env.example` to `.env` and fill in your credentials for at least one service (see below):
   ```bash
   cp .env.example .env
   ```
2. Run:
   ```bash
   python start.py
   ```

That's it. The launcher will create a virtual environment, install all dependencies, start the Flask server, and open a live preview in your browser at `http://127.0.0.1:5000/preview`.

Press **Ctrl+C** to stop the server. Pass `--no-open` to skip opening the browser.

---

## Option 1: Spotify API (Recommended)

### Spotify API App

- Create a [Spotify Application](https://developer.spotify.com/dashboard/applications)
- Take note of:
  - `Client ID`
  - `Client Secret`
- Click on **Edit Settings**
- In **Redirect URIs**:
  - Add `https://example.com/callback`

## Refresh Token

### Script (recommended)

Requires only Python 3.9+, no extra packages:

```bash
python scripts/get_token.py
```

The script:

1. Asks for your `Client ID` and `Client Secret` (or reads `SPOTIFY_CLIENT_ID` / `SPOTIFY_SECRET_ID` from the environment)
2. Opens Spotify's authorization page in your browser
3. Asks you to paste the **full URL** you are redirected to (`https://example.com/callback?code=...`). The page itself won't load; that's expected
4. Prints the two lines to set on Vercel:

```text
SPOTIFY_REFRESH_TOKEN=AQ...
SPOTIFY_REFRESH_TOKEN_DATE=2026-10-29
```

> [!IMPORTANT]
> **Authorization code ≠ refresh token.** The `code=` value in the callback URL is single-use and expires in minutes; it's only exchanged for the refresh token. Never put the code in `SPOTIFY_REFRESH_TOKEN`.

### Manual

- Navigate to the following URL:

```
https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&scope=user-read-currently-playing,user-read-recently-played&redirect_uri=https://example.com/callback
```

- After logging in, save the {CODE} portion of: `https://example.com/callback?code={CODE}`

- Create a string combining `{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}` (e.g. `5n7o4v5a3t7o5r2e3m1:5a8n7d3r4e2w5n8o2v3a7c5`) and **encode** into [Base64](https://base64.io/).

- Then run a [curl command](https://httpie.org/run) in the form of:

```sh
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Basic {BASE64}" -d "grant_type=authorization_code&redirect_uri=https://example.com/callback&code={CODE}" https://accounts.spotify.com/api/token
```

> On Windows PowerShell, type `curl.exe` instead of `curl`: plain `curl` is an alias of `Invoke-WebRequest` and fails with these flags.

- Save the `refresh_token` field of the JSON response (not the `access_token`, which lasts one hour), and today's date as `SPOTIFY_REFRESH_TOKEN_DATE`

## Token expiration

Since July 20, 2026, Spotify refresh tokens **expire 6 months after you authorize the app**, and using them does not extend that deadline ([announcement](https://developer.spotify.com/blog/2026-06-18-refresh-token-expiration)). After that, the widget shows the *Spotify token expired* card (see [Error cards](#error-cards)).

Also, apps in Development Mode only work while the app owner has an **active Spotify Premium** subscription.

To renew:

1. Run `python scripts/get_token.py`
2. On Vercel, update `SPOTIFY_REFRESH_TOKEN` and `SPOTIFY_REFRESH_TOKEN_DATE` with the printed values
3. Redeploy the project (Deployments → ⋯ → Redeploy) so the new values take effect

`SPOTIFY_REFRESH_TOKEN_DATE` is optional, but with it `/health/auth` tells you how many days are left (see [Health Check Endpoints](#health-check-endpoints)).

---

## Option 2: Last.fm API

Last.fm is a simpler alternative that doesn't require OAuth setup. It only requires an API key and username.

### Get Last.fm API Key

1. Go to [Last.fm API Account Creation](https://www.last.fm/api/account/create)
2. Fill in the application details:
   - **Application name**: Choose any name (e.g., "Now Playing Widget")
   - **Application description**: Brief description
   - **Application homepage**: Can be your GitHub profile or repo URL
   - **Callback URL**: Leave empty or use any URL (not used for this project)
3. Click **Submit**
4. Take note of:
   - `API Key` (this becomes `LAST_FM_API_KEY`)

### Get Your Last.fm Username

Your username is the one you use to log in to Last.fm. You can find it:
- In your profile URL: `https://www.last.fm/user/{YOUR_USERNAME}`
- This becomes `LAST_FM_USERNAME`

### Environment Variables for Last.fm

You'll need these two environment variables:
- `LAST_FM_API_KEY` - Your Last.fm API key
- `LAST_FM_USERNAME` - Your Last.fm username

---

## Deployment

### Deploy to Vercel

- Register on [Vercel](https://vercel.com/)

- Fork this repo, then create a vercel project linked to it

- Add Environment Variables:

  - `https://vercel.com/<YourName>/<ProjectName>/settings/environment-variables`
  
  **For Spotify:**
    - `SPOTIFY_REFRESH_TOKEN`
    - `SPOTIFY_CLIENT_ID`
    - `SPOTIFY_SECRET_ID`
    - `SPOTIFY_REFRESH_TOKEN_DATE` (optional, enables the expiry countdown in `/health/auth`)
  
  **For Last.fm:**
    - `LAST_FM_API_KEY`
    - `LAST_FM_USERNAME`

- Deploy!

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https%3A%2F%2Fgithub.com%2Fnovatorem%2Fnovatorem)

- Create a Heroku application via the Heroku CLI or via the Heroku Dashboard. Connect the app with your GitHub repository and enable automatic builds <br>
  `PS. automatic build means that everytime you push changes to remote, heroku will rebuild and redeploy the app.`
  - To start the Flask server execute `heroku ps:scale web=1` once the build is completed.
- Or click the `Deploy to Heroku` button above to automatically start the deployment process.

### Run locally with Docker (alternative)

If you prefer Docker over the `python start.py` launcher:

```bash
docker compose up
```

Then open [http://localhost:5000/preview](http://localhost:5000/preview). Stop with `docker compose down`.

## ReadMe

You can now use the following in your readme:

**For Spotify users:**

`[![Spotify](https://music-player-widget-ten.vercel.app/api/spotify/)](https://open.spotify.com/user/USER_NAME)`

**For Last.fm users:**

`[![Last.fm](https://music-player-widget-ten.vercel.app/api/spotify/)](https://www.last.fm/user/USER_NAME)`

## Customization

### URL Parameters

You can customize the appearance of your widget using URL query parameters:

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `background_color` | Card background color (hex, without `#`) | `181414` | `0d1117` |
| `border_color` | Card border color (hex, without `#`) | `181414` | `ffffff` |
| `background_type` | Background style: `color`, `blur_dark`, or `blur_light` | `color` | `blur_dark` |
| `show_status` | Show "Vibing to:" or "Recently played:" text | `false` | `true` |
| `compact` | Smaller 400x80 layout | `false` | `true` |
| `theme` | Theme for this URL (overrides `current-theme`, see [Theme Templates](#theme-templates)) | `current-theme` | `stardew` |
| `lang` | Language of the [error cards](#error-cards): `en` or `pt-BR` | `en` | `pt-BR` |

#### Background Types

- **`color`** - Solid color background (default)
- **`blur_dark`** - Blurred album art with dark overlay (great for dark themes)
- **`blur_light`** - Blurred album art with light overlay (great for light themes)

#### Examples

Basic dark theme:
```
https://music-player-widget-ten.vercel.app/api/spotify/
```

Custom colors:
```
https://music-player-widget-ten.vercel.app/api/spotify/?background_color=0d1117&border_color=30363d
```

**Blurred album art background (dark):**
```
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_dark
```

**Blurred album art background (light):**
```
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_light
```

With status text:
```
https://music-player-widget-ten.vercel.app/api/spotify/?show_status=true
```

Full customization with blur:
```
https://music-player-widget-ten.vercel.app/api/spotify/?background_type=blur_dark&border_color=333333&show_status=true
```

**Stardew theme** (with and without status, also works with `compact=true`):
```
https://music-player-widget-ten.vercel.app/api/spotify/?theme=stardew
https://music-player-widget-ten.vercel.app/api/spotify/?theme=stardew&show_status=true
```

### Theme Templates

Change the widget theme by editing the `current-theme` property in `api/templates.json`:

```json
{
    "current-theme": "dark",
    "templates": {
        "light": "spotify.html.j2",
        "dark": "spotify-dark.html.j2",
        "stardew": "stardew.html.j2",
        "base": "base.html.j2"
    }
}
```

Any key under `templates` can also be picked per URL with `?theme=<key>`; unknown values fall back to `current-theme`.

Available themes:
- `light` - Transparent background, no border
- `dark` - Customizable background and border colors
- `stardew` - Pixel-art dialogue box with an embedded pixel font. Fixed look: ignores `background_color`, `border_color` and `background_type`

Themes that need fonts or images (like `stardew`) keep them in `api/assets/` and register them in `THEME_ASSETS` (`api/theme_assets.py`): the SVG is shown through `<img>`, so every asset is embedded as base64. Layout changes (thicker border, bigger fonts) go in `THEME_LAYOUTS` (`api/config.py`), so the equalizer bars stay aligned.

### Creating Custom Themes

To create your own theme:

1. Create a new template file in `api/templates/` that extends `base.html.j2`:

```jinja2
{% extends "base.html.j2" %}

{% block container_styles %}
/* Your container styles */
background-color: var(--background-color);
border: 2px solid var(--border-color);
{% endblock %}

{% block theme_styles %}
/* Your custom CSS overrides */
.song {
    font-weight: 700;
}
{% endblock %}
```

2. Add your theme to `templates.json`:

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

### Health Check Endpoints

**`/health`**: liveness check. Returns `OK` while the server is up (used by the Docker healthcheck).

```
https://music-player-widget-ten.vercel.app/api/spotify/health
```

**`/health/auth`**: runs a real authentication against the configured service and returns JSON. Status `200` when auth works, `503` when it fails or nothing is configured. Results are cached for 5 minutes.

```
https://music-player-widget-ten.vercel.app/api/spotify/health/auth
```

```json
{"service": "spotify", "status": "ok", "token_date": "2026-10-29", "expires_on": "2027-04-29", "days_remaining": 182}
```

| Field | Meaning |
|-------|---------|
| `service` | `spotify`, `lastfm` or `null` |
| `status` | `ok` or `error` |
| `error` | Only on failure: the same code as the [error card](#common-errors) |
| `token_date` / `expires_on` / `days_remaining` | From `SPOTIFY_REFRESH_TOKEN_DATE`; `null` when it isn't set (and always on Last.fm) |
| `warning` | `invalid_token_date` when `SPOTIFY_REFRESH_TOKEN_DATE` isn't `YYYY-MM-DD` |

To get warned before the token expires, point any scheduled job (cron, GitHub Actions in your profile repo, an uptime monitor) at it. For example, this fails when auth is broken or fewer than 30 days are left:

```bash
curl -fsS https://<your-deploy>/api/spotify/health/auth | jq -e '.days_remaining == null or .days_remaining > 30'
```

### Audio-Reactive Animations

The equalizer bars automatically sync to the music's characteristics:

**For Spotify users:**
- Bars pulse at the actual **BPM** of the song
- Animation intensity scales with the track's **energy** level
- Animation curves adjust based on **danceability**
- High-energy tracks have more dramatic bar movements and subtle album art pulsing

**For Last.fm users:**
- If you also have Spotify configured, the widget will look up the track on Spotify to get audio features
- Otherwise, sensible defaults are used (120 BPM, medium energy)

This creates a unique visual experience for each track - calm songs have gentler animations, while energetic tracks have more dynamic, punchy visuals.

## Error cards

When something is wrong with the setup, the widget doesn't turn into a broken image on your README. It shows a card in the widget's own style saying what happened and what to do, in the language set by `?lang=` (`en` or `pt-BR`), with your colors and size parameters:

![Spotify token expired](https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=token_expired&lang=en)

```
https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=token_expired&lang=en
```

![Widget not configured](https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=not_configured&lang=en&compact=true)

```
https://music-player-widget-ten.vercel.app/api/spotify/preview/error?code=not_configured&lang=en&compact=true
```

`/preview/error?code=<code>` renders any card from the table below on your own deploy without calling Spotify, so you can see how each one looks with your parameters.

To diagnose your setup:

1. Open your widget URL in the browser and read the card
2. Or check the `X-Widget-Error` response header: `curl -sI "https://<your-deploy>/api/spotify/" | grep -i x-widget-error`
3. Open `/health/auth` (see [Health Check Endpoints](#health-check-endpoints))
4. Find the code below

### Common errors

| Card (`X-Widget-Error`) | Cause | Fix |
|-------------------------|-------|-----|
| Widget not configured (`not_configured`) | No `SPOTIFY_*` or `LAST_FM_*` variables | Set the variables on Vercel and redeploy |
| Spotify token expired (`token_expired`) | Refresh token older than 6 months, or revoked | [Renew it](#token-expiration) with `scripts/get_token.py` |
| Invalid Spotify credentials (`invalid_client`) | Wrong `SPOTIFY_CLIENT_ID` or `SPOTIFY_SECRET_ID` | Copy them again from the Spotify dashboard (watch for extra spaces) |
| Spotify authentication failed (`auth_failed`) | Spotify rejected the token request for another reason | Check the `[spotify] token refresh failed` line in the Vercel logs |
| Spotify access denied (`premium_required`) | Development Mode app whose owner has no active Premium, or your account isn't in the app's user list | Renew Premium on the app owner's account; add your account under **User Management** in the dashboard |
| Music service unavailable (`service_unavailable`) | Spotify or Last.fm is down or unreachable | Nothing to fix on your side; it recovers on its own |
| Music service error (`api_error`) | Unexpected API response | Check the Vercel logs |
| No song to show right now (`no_tracks`) | A podcast or other non-music content is playing and there's no recent song | Play a song; the widget updates on the next load |
| Something went wrong (`unknown`) | Unexpected error | Check the Vercel logs; open an issue if it persists |

## Debugging

If you have issues setting up, try following this [guide](https://youtu.be/n6d4KHSKqGk?t=615).

Followed the guide and still having problems?
Try checking out the functions tab in vercel, linked as:
`https://vercel.com/{name}/spotify/{build}/functions`

<details><summary>Which looks like-</summary>

![image](https://user-images.githubusercontent.com/16753077/91338931-b0326680-e7a3-11ea-8178-5499e0e73250.png)

</details><br>

You will see a log there, and most issues can be resolved by ensuring you have the correct variables from setup.

Error details are logged there too: a failed token refresh logs `[spotify] token refresh failed: HTTP <status> <Spotify response>`.

**Running locally behind a corporate proxy?** If requests fail with SSL certificate errors, point Python at your company's certificate bundle:

```bash
export REQUESTS_CA_BUNDLE=/path/to/company-ca.pem   # PowerShell: $env:REQUESTS_CA_BUNDLE = "C:\path\to\company-ca.pem"
```
