#!/usr/bin/env python3
"""
build_posts.py — Convierte posts Markdown a HTML estático.
Genera:
  - posts-built/{lang}/{slug}.html (páginas individuales)
  - posts/index.json (índice para el frontend)
  - feed.xml (RSS 2.0)

Uso:
  python3 scripts/build_posts.py
"""

import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from xml.dom import minidom

# Intentar importar markdown
try:
    import markdown
except ImportError:
    print("❌ markdown no instalado. Ejecutá: pip install markdown")
    sys.exit(1)


# ============================================================
# Configuración
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "posts"
OUTPUT_DIR = PROJECT_ROOT / "posts-built"
SITE_URL = "https://jmartinez.dev"
LANG_MAP = {"es": "es", "en": "en"}

# Template para post individual
POST_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Juan Sebastián Martínez</title>
<link rel="stylesheet" href="../styles.css">
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<link rel="alternate" hreflang="es" href="{site_url}/posts-built/es/{slug}.html">
<link rel="alternate" hreflang="en" href="{site_url}/posts-built/en/{slug}.html">
</head>
<body>

<nav>
  <div class="nav-logo">JSM_SEC // v2025.2</div>
  <ul class="nav-links">
    <li><a href="../index.html">Inicio</a></li>
    <li><a href="../blog.html">Blog</a></li>
    <li><a href="../index.html#contacto">Contacto</a></li>
  </ul>
</nav>

<div id="hero" style="min-height:30vh;padding:120px 48px 40px">
  <div class="hero-inner">
    <div class="hero-tag">{date}</div>
    <h1>{title}</h1>
  </div>
</div>

<article style="max-width:800px;margin:0 auto;padding:0 48px 80px;color:#B0C4D8;font-size:16px;line-height:1.8">
{body}
</article>

<footer>
  <div>Juan Sebastián Martínez · Asunción, Paraguay</div>
  <div style="margin-top:8px;font-size:11px">Cybersecurity Architect · AI Infrastructure</div>
</footer>

</body>
</html>"""


# ============================================================
# Parser de frontmatter
# ============================================================

def parse_frontmatter(content: str) -> dict:
    """Parsea frontmatter YAML simple (sin dependencia PyYAML)."""
    fm = {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return fm, content

    yaml_block = parts[1].strip()
    body = parts[2].strip()

    for line in yaml_block.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Parsear tipos
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            fm[key] = value

    return fm, body


# ============================================================
# Build
# ============================================================

def build_all():
    """Procesa todos los posts y genera archivos."""
    posts_index = []
    post_items = []  # Para RSS

    # Limpiar output
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for f in OUTPUT_DIR.iterdir():
        if f.is_dir():
            import shutil
            shutil.rmtree(f)

    posts = sorted(POSTS_DIR.iterdir())

    for post_dir in posts:
        if not post_dir.is_dir() or post_dir.name.startswith("."):
            continue

        for md_file in sorted(post_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(content)

            if not fm.get("title"):
                print(f"⚠️  Saltando {md_file}: sin título en frontmatter")
                continue

            # Convertir Markdown a HTML
            html_body = markdown.markdown(
                body,
                extensions=["fenced_code", "codehilite", "tables"]
            )

            lang = fm.get("lang", "es")
            slug = fm.get("slug", post_dir.name)
            title = fm["title"]
            description = fm.get("description", "")
            date = fm.get("date", "")
            tags = fm.get("tags", [])

            # Generar HTML del post
            post_html = POST_TEMPLATE.format(
                lang=lang,
                title=title,
                description=description.replace('"', "&quot;"),
                date=date,
                slug=slug,
                body=html_body,
                site_url=SITE_URL,
            )

            # Escribir archivo
            out_dir = OUTPUT_DIR / lang
            os.makedirs(out_dir, exist_ok=True)
            out_path = out_dir / f"{slug}.html"
            out_path.write_text(post_html, encoding="utf-8")
            print(f"✅ {out_path} ({lang})")

            # Agregar al índice
            posts_index.append({
                "slug": slug,
                "title": title,
                "description": description,
                "date": date,
                "lang": lang,
                "tags": tags if isinstance(tags, list) else [tags],
            })

            # Para RSS (solo EN para el feed principal)
            if lang == "en":
                post_items.append({
                    "title": title,
                    "description": description,
                    "date": date,
                    "slug": slug,
                    "link": f"{SITE_URL}/posts-built/en/{slug}.html",
                })

    # Escribir índice JSON
    index_path = POSTS_DIR / "index.json"
    index_path.write_text(json.dumps(posts_index, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✅ Índice: {index_path} ({len(posts_index)} posts)")

    # Generar RSS
    generate_rss(post_items)
    generate_feed_xml(posts_index)

    return len(posts_index)


def generate_rss(items):
    """Genera feed RSS 2.0."""
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Juan Sebastián Martínez — Blog"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "Artículos sobre ciberseguridad, AI infrastructure y orquestación de agentes."
    ET.SubElement(channel, "language").text = "en"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    for item in items[:10]:  # Últimos 10
        it = ET.SubElement(channel, "item")
        ET.SubElement(it, "title").text = item["title"]
        ET.SubElement(it, "link").text = item["link"]
        ET.SubElement(it, "description").text = item["description"]
        ET.SubElement(it, "pubDate").text = item["date"] + "T00:00:00+0000" if "T" not in item["date"] else item["date"]

    rough_string = ET.tostring(rss, encoding="unicode")
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    rss_path = PROJECT_ROOT / "feed.xml"
    rss_path.write_text(pretty, encoding="utf-8")
    print(f"✅ RSS: {rss_path}")


def generate_feed_xml(posts_index):
    """Genera feed.xml alternativo con todos los posts."""
    pass  # Por ahora el RSS es suficiente


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("🔨 Build de posts\n")
    count = build_all()
    print(f"\n📊 Total: {count} posts generados")
