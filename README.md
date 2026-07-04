# jsm-portfolio

Portfolio personal de Juan Sebastián Martínez — Cybersecurity Architect & AI Infrastructure

**Deploy:** GitHub Pages → https://jmartinez.dev
**Self-hosted (opcional):** Docker + Nginx + Certbot

## Estructura
- `index.html` - HTML principal
- `styles.css` - Estilos minificados
- `assets/` - favicon, og-image, CV.pdf
- `robots.txt`, `sitemap.xml`, `CNAME`
- `.github/workflows/deploy.yml` - CI/CD GitHub Actions
- `nginx/` - Configuración self-hosted (Docker, Nginx, Certbot)

## Desarrollo local
```bash
npm install
npm run lint
npm run serve
```

## CI/CD
Push a `main` → GitHub Actions → Deploy a GitHub Pages
