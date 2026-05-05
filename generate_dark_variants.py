#!/usr/bin/env python3
"""Generate dark-mode SVG variants and a live stats card."""
import os

def generate_stats_card():
    bars = [
        ("Python", 220, 62),
        ("JavaScript", 180, 32),
        ("Kotlin", 56, 6),
    ]

    defs = '''<defs>
    <filter id="glow"><feGaussianBlur stdDeviation="2.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#FFD700" stop-opacity="0.4"/><stop offset="100%" stop-color="#C9A84C" stop-opacity="0.9"/></linearGradient>
    <linearGradient id="shimmer" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#000000" stop-opacity="0"/><stop offset="40%" stop-color="#FFD700" stop-opacity="0.08"/><stop offset="50%" stop-color="#FFD700" stop-opacity="0.35"/><stop offset="60%" stop-color="#FFD700" stop-opacity="0.08"/><stop offset="100%" stop-color="#000000" stop-opacity="0"/></linearGradient>
  </defs>'''

    # Stats boxes
    stats = [
        ("REPOSITORIES", "32", 40),
        ("COMMITS", "500+", 190),
        ("STARS", "* 100+", 340),
        ("PULL REQUESTS", "85+", 490),
        ("BUILD STREAK", "90+", 660),
    ]
    stats_svg = ""
    for label, val, x in stats:
        dur = f"{3 + (hash(val) % 20)/10:.1f}s"
        stats_svg += f'''
  <g transform="translate({x}, 65)">
    <text font-family="Georgia, serif" font-size="11" fill="#8b949e" letter-spacing="2">{label}</text>
    <text font-family="Georgia, serif" font-size="28" font-weight="bold" fill="#FFD700" y="26" filter="url(#glow)">
      {val}
      <animate attributeName="fill-opacity" values="0.8;1;0.8" dur="{dur}" repeatCount="indefinite"/>
    </text>
  </g>'''

    language_svg = ""
    for i, (lang, w, pct) in enumerate(bars):
        delay = i * 0.2
        language_svg += f'''
    <text font-family="Georgia, serif" font-size="13" fill="#c9d1d9" y="{24 + i*20}">{lang}</text>
    <rect x="90" y="{15 + i*20}" width="280" height="8" rx="4" fill="#161b22"/>
    <rect x="90" y="{15 + i*20}" width="{w}" height="8" rx="4" fill="url(#barGrad)">
      <animate attributeName="width" values="0;{w}" dur="1.5s" begin="{delay}s" fill="freeze"/>
    </rect>
    <text font-family="Georgia, serif" font-size="10" fill="#FFD700" x="380" y="{24 + i*20}">{pct}%</text>'''

    dark = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="850" height="220" viewBox="0 0 850 220">
  {defs}
  <rect width="850" height="220" fill="#000000"/>
  <text x="40" y="32" font-family="Georgia, serif" font-size="16" font-weight="bold" fill="#FFD700" letter-spacing="3">
    Omega VERITAS - Live Telemetry
    <animate attributeName="fill-opacity" values="0.6;1;0.6" dur="4s" repeatCount="indefinite"/>
  </text>
  <line x1="40" y1="42" x2="810" y2="42" stroke="#30363d" stroke-width="1"/>
  {stats_svg}
  <g transform="translate(40, 130)">
    <text font-family="Georgia, serif" font-size="11" fill="#8b949e" letter-spacing="2">PRIMARY LANGUAGES</text>
    {language_svg}
  </g>
  <g transform="translate(600, 110)">
    <text font-family="Georgia, serif" font-size="11" fill="#8b949e" letter-spacing="2" text-anchor="middle">ECOSYSTEM</text>
    <g opacity="0.3">
      <ellipse cx="0" cy="45" rx="60" ry="45" fill="none" stroke="#FFD700" stroke-width="0.5">
        <animateTransform type="rotate" from="0 0 45" to="360 0 45" dur="60s" repeatCount="indefinite"/>
      </ellipse>
      <ellipse cx="0" cy="45" rx="40" ry="32" fill="none" stroke="#FFD700" stroke-width="0.5">
        <animateTransform type="rotate" from="360 0 45" to="0 0 45" dur="45s" repeatCount="indefinite"/>
      </ellipse>
      <ellipse cx="0" cy="45" rx="20" ry="16" fill="none" stroke="#FFD700" stroke-width="0.5">
        <animateTransform type="rotate" from="0 0 45" to="360 0 45" dur="30s" repeatCount="indefinite"/>
      </ellipse>
    </g>
    <text x="-5" y="55" font-family="Georgia, serif" font-size="28" font-weight="bold" fill="#FFD700" opacity="0.8">
      Omega
      <animate attributeName="fill-opacity" values="0.5;0.9;0.5" dur="3s" repeatCount="indefinite"/>
    </text>
  </g>
  <rect x="0" y="210" width="850" height="10" fill="#000000"/>
  <rect x="-100" y="210" width="300" height="10" fill="url(#shimmer)">
    <animateTransform type="translate" values="-300,0; 1000,0" dur="8s" repeatCount="indefinite"/>
  </rect>
</svg>'''

    light = dark.replace('fill="#000000"', 'fill="#0d1117"')
    light = light.replace('fill="#161b22"', 'fill="#21262d"')
    light = light.replace('fill="#8b949e"', 'fill="#6e7781"')
    light = light.replace('fill="#c9d1d9"', 'fill="#24292e"')
    light = light.replace('fill="#30363d"', 'fill="#d0d7de"')
    light = light.replace('#000000', '#ffffff')
    light = light.replace('-0.4;', '-0.4;')

    return dark, light

if __name__ == '__main__':
    dark_svg, light_svg = generate_stats_card()
    with open('github-stats-card-dark.svg', 'w') as f:
        f.write(dark_svg)
    with open('github-stats-card.svg', 'w') as f:
        f.write(light_svg)
    print('[DONE] github-stats-card.svg + dark.svg generated')
