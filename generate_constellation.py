#!/usr/bin/env python3
"""
VERITAS Omega Constellation — Live Ecosystem Mapper
Fetches repo metadata from GitHub API, regenerates omega-constellation.svg
with real star positions, activity levels, and connection threads.

Usage: python3 generate_constellation.py [--output PATH] [--token GITHUB_TOKEN]
"""

import json
import math
import os
import sys
import urllib.request
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape

# ── Configuration ──────────────────────────────────────────────
GITHUB_USER = "VrtxOmega"
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "omega-constellation.svg")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_API = f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&sort=pushed"

# Core repos that get bigger stars and anchor the constellation
CORE_REPOS = {
    "omega-brain-mcp": {"label": "Governance Core · AAA", "tier": "core"},
    "Ollama-Omega": {"label": "Sovereign Bridge", "tier": "major"},
    "Gravity-Omega": {"label": "AI-Powered IDE", "tier": "major"},
    "Aegis": {"label": "Security Suite", "tier": "major"},
    "OmegaWallet": {"label": "Desktop Wallet · 141/141", "tier": "major"},
    "SovereignMedia": {"label": "Shipped Product", "tier": "major"},
    "veritas-portfolio": {"label": "Evidence Index", "tier": "minor"},
    "hermes-sentinel": {"label": "Security MCP", "tier": "minor"},
    "sovereign-arcade": {"label": "Games Platform", "tier": "minor"},
    "sovereign-docs": {"label": "VERITAS Documentation", "tier": "minor"},
    "sswp-registry": {"label": "SSWP Registry", "tier": "minor"},
    "omega-brain-mcp-server": {"label": "MCP Protocol", "tier": "minor"},
}

# Star positions on the canvas (800x440, center at 400,230)
STAR_POSITIONS = {
    "omega-brain-mcp":      (260, 170),
    "Ollama-Omega":         (540, 150),
    "Gravity-Omega":        (400, 80),
    "Aegis":                (220, 330),
    "OmegaWallet":          (580, 310),
    "SovereignMedia":       (660, 210),
    "veritas-portfolio":    (130, 190),
    "hermes-sentinel":      (160, 100),
    "sovereign-arcade":     (620, 90),
    "sovereign-docs":       (400, 380),
    "sswp-registry":        (680, 320),
    "omega-brain-mcp-server": (300, 130),
}

# Connection pairs (repo pairs that have threads between them)
CONNECTIONS = [
    ("omega-brain-mcp", "Ollama-Omega"),
    ("Ollama-Omega", "Gravity-Omega"),
    ("Gravity-Omega", "Aegis"),
    ("Aegis", "hermes-sentinel"),
    ("OmegaWallet", "SovereignMedia"),
    ("veritas-portfolio", "sovereign-docs"),
    ("omega-brain-mcp", "omega-brain-mcp-server"),
    ("sswp-registry", "omega-brain-mcp"),
]

SVG_WIDTH = 800
SVG_HEIGHT = 440
CENTER_X = 400
CENTER_Y = 230

# ── Helpers ─────────────────────────────────────────────────────

def fetch_repos():
    """Fetch all repos from GitHub API."""
    req = urllib.request.Request(GITHUB_API, headers={
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "VERITAS-Constellation/1.0"
    })
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"Bearer {GITHUB_TOKEN}")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[WARN] GitHub API unreachable: {e}", file=sys.stderr)
        return []


def star_size(repo_name, tier, recent_push_days):
    """Calculate star radius from repo importance and recency."""
    base = {"core": 5.0, "major": 4.5, "minor": 3.5}
    r = base.get(tier, 3.0)
    # Boost for recently pushed repos (within 7 days)
    if recent_push_days < 7:
        r += 0.5
    if recent_push_days < 3:
        r += 0.5
    return r


def connection_pairs(repo_names):
    """Return connections where both repos exist."""
    names_set = set(repo_names)
    return [(a, b) for a, b in CONNECTIONS if a in names_set and b in names_set]


# ── SVG Generation ─────────────────────────────────────────────


def svg_defs():
    return """  <defs>
    <filter id="starGlow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="coreGlow">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="threadGlow">
      <feGaussianBlur stdDeviation="1" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="coreAura" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#FFD700" stop-opacity="0.15"/>
      <stop offset="50%" stop-color="#FFD700" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>"""


def generate_svg(repos):
    """Generate the full constellation SVG."""
    now = datetime.utcnow()
    repo_count = len(repos)
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    has_glama_aaa = True  # we have AAA repos

    # Map repo names to their data
    repo_map = {}
    for r in repos:
        name = r.get("name", "")
        pushed = r.get("pushed_at", "")
        recent_days = 999
        if pushed:
            try:
                pushed_dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ")
                recent_days = (now - pushed_dt).days
            except:
                pass
        repo_map[name] = {
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "recent_days": recent_days,
            "description": r.get("description", "") or "",
            "language": r.get("language", "") or "",
        }

    # Build SVG parts
    parts = []

    # Header
    parts.append(f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" width="{SVG_WIDTH}" height="{SVG_HEIGHT}">""")
    parts.append(svg_defs())

    # Background
    parts.append(f'  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="#000000"/>')

    # Title
    parts.append(f'  <text x="{CENTER_X}" y="28" font-family="Georgia, serif" font-size="14" fill="#C9A84C" text-anchor="middle" letter-spacing="4" fill-opacity="0.7">Ω UNIVERSE CONSTELLATION</text>')

    # Core aura
    parts.append(f'  <ellipse cx="{CENTER_X}" cy="{CENTER_Y}" rx="120" ry="100" fill="url(#coreAura)">')
    parts.append('    <animate attributeName="rx" values="120;135;120" dur="4s" repeatCount="indefinite"/>')
    parts.append('    <animate attributeName="ry" values="100;110;100" dur="4s" repeatCount="indefinite"/>')
    parts.append('  </ellipse>')

    # Connection threads
    active_connections = connection_pairs(list(repo_map.keys()))
    if active_connections:
        parts.append('  <g filter="url(#threadGlow)" stroke="#FFD700" stroke-width="0.5" stroke-opacity="0.25" fill="none">')
        parts.append('    <animate attributeName="stroke-opacity" values="0.25;0.4;0.25" dur="5s" repeatCount="indefinite"/>')
        i = 0
        for a_name, b_name in active_connections:
            if a_name in STAR_POSITIONS and b_name in STAR_POSITIONS:
                x1, y1 = STAR_POSITIONS[a_name]
                x2, y2 = STAR_POSITIONS[b_name]
                opacity = "0.25" if i == 0 else "0.15"
                parts.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-opacity="{opacity}">')
                if i == 0:
                    parts.append('      <animate attributeName="stroke-opacity" values="0.25;0.5;0.25" dur="3.7s" repeatCount="indefinite"/>')
                parts.append('    </line>')
                i += 1

        # Connections from stars to core
        for name in repo_map:
            if name in STAR_POSITIONS and name != "omega-brain-mcp" and name != "omega-brain-mcp-server":
                x, y = STAR_POSITIONS[name]
                parts.append(f'    <line x1="{x}" y1="{y}" x2="{CENTER_X}" y2="{CENTER_Y}" stroke-opacity="0.12"/>')

        parts.append('  </g>')

    # Orbit rings
    parts.append('  <g fill="none" stroke="#FFD700" stroke-width="0.3" stroke-opacity="0.10">')
    parts.append(f'    <ellipse cx="{CENTER_X}" cy="{CENTER_Y}" rx="200" ry="160">')
    parts.append(f'      <animateTransform attributeName="transform" type="rotate" from="0 {CENTER_X} {CENTER_Y}" to="360 {CENTER_X} {CENTER_Y}" dur="60s" repeatCount="indefinite"/>')
    parts.append('    </ellipse>')
    parts.append(f'    <ellipse cx="{CENTER_X}" cy="{CENTER_Y}" rx="100" ry="80">')
    parts.append(f'      <animateTransform attributeName="transform" type="rotate" from="360 {CENTER_X} {CENTER_Y}" to="0 {CENTER_X} {CENTER_Y}" dur="40s" repeatCount="indefinite"/>')
    parts.append('    </ellipse>')
    parts.append('  </g>')

    # Center Ω core
    parts.append('  <g filter="url(#coreGlow)">')
    parts.append(f'    <text x="{CENTER_X}" y="240" font-family="Georgia, serif" font-size="36" fill="#FFD700" text-anchor="middle" font-weight="bold">Ω')
    parts.append('      <animate attributeName="font-size" values="36;38;36" dur="4s" repeatCount="indefinite"/>')
    parts.append('      <animate attributeName="fill-opacity" values="0.9;1;0.9" dur="4s" repeatCount="indefinite"/>')
    parts.append('    </text>')
    parts.append(f'    <text x="{CENTER_X}" y="258" font-family="Georgia, serif" font-size="9" fill="#C9A84C" text-anchor="middle" letter-spacing="2" fill-opacity="0.7">VERITAS CORE</text>')
    parts.append('  </g>')

    # Stars for each known repo
    for name, info in repo_map.items():
        if name not in STAR_POSITIONS:
            continue
        tier = CORE_REPOS.get(name, {}).get("tier", "minor")
        label = CORE_REPOS.get(name, {}).get("label", info["description"][:40])
        x, y = STAR_POSITIONS[name]
        r = star_size(name, tier, info["recent_days"])
        font_size = 10 if tier in ("core", "major") else 9
        label_font_size = 8 if tier in ("core", "major") else 7

        # Random-ish animation duration
        dur = round(2.5 + hash(name) % 15 * 0.1, 1)
        parts.append(f'  <g filter="url(#starGlow)">')
        parts.append(f'    <circle cx="{x}" cy="{y}" r="{r}" fill="#FFD700">')
        parts.append(f'      <animate attributeName="r" values="{r};{r+2};{r}" dur="{dur}s" repeatCount="indefinite"/>')
        parts.append(f'    </circle>')
        parts.append(f'    <text x="{x}" y="{y-15}" font-family="Georgia, serif" font-size="{font_size}" fill="#FFD700" text-anchor="middle" fill-opacity="0.9">{xml_escape(name)}</text>')
        if label:
            parts.append(f'    <text x="{x}" y="{y+22}" font-family="Georgia, serif" font-size="{label_font_size}" fill="#C9A84C" text-anchor="middle" fill-opacity="0.6">{xml_escape(label)}</text>')
        parts.append(f'  </g>')

    # Bottom metrics bar
    parts.append(f'  <g font-family="Georgia, serif" fill="#C9A84C" text-anchor="middle">')
    parts.append(f'    <text x="200" y="430" font-size="10" fill-opacity="0.6">')
    parts.append(f'      <tspan fill="#FFD700" fill-opacity="0.9" font-size="14">{repo_count}</tspan> REPOSITORIES')
    parts.append(f'    </text>')
    parts.append(f'    <text x="{CENTER_X}" y="430" font-size="10" fill-opacity="0.6">')
    parts.append(f'      <tspan fill="#FFD700" fill-opacity="0.9" font-size="14">10</tspan> GATES')
    parts.append(f'    </text>')
    parts.append(f'    <text x="600" y="430" font-size="10" fill-opacity="0.6">')
    parts.append(f'      <tspan fill="#FFD700" fill-opacity="0.9" font-size="14">{"AAA" if has_glama_aaa else "—"}</tspan> GLAMA RATING')
    parts.append(f'    </text>')
    parts.append(f'  </g>')

    # End
    parts.append('</svg>')
    return '\n'.join(parts)


# ── Main ────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="VERITAS Omega Constellation generator")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="Output SVG path")
    parser.add_argument("--token", help="GitHub personal access token (or use GITHUB_TOKEN env)")
    args = parser.parse_args()

    # Set token
    global GITHUB_TOKEN
    if args.token:
        GITHUB_TOKEN = args.token

    print(f"[VERITAS] Fetching repos for {GITHUB_USER}...")
    repos = fetch_repos()
    if not repos:
        print("[WARN] No repos fetched — generating static fallback, skipping core stars.")
        # Fallback: use CORE_REPOS keys as minimal data
        repos = [{"name": name, "stargazers_count": 0, "forks_count": 0, "pushed_at": "", "description": "", "language": ""} for name in STAR_POSITIONS]

    print(f"[VERITAS] Generating constellation with {len(repos)} repos...")
    svg_content = generate_svg(repos)

    # Ensure output dir exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w") as f:
        f.write(svg_content)
    print(f"[VERITAS] Constellation written → {args.output}")


if __name__ == "__main__":
    main()
