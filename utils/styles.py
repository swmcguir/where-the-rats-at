"""
Shared styles for Where the Rats At? - Design System v3.0
Monochrome editorial design: black hero panels, white body, hairline borders,
big grotesque type. Color is reserved for grades and status only.
"""

# Grade color palette with extended variants
GRADE_COLORS = {
    'A': {'main': '#10b981', 'light': '#d1fae5', 'dark': '#065f46', 'glow': 'rgba(16, 185, 129, 0.3)'},
    'B': {'main': '#84cc16', 'light': '#ecfccb', 'dark': '#3f6212', 'glow': 'rgba(132, 204, 22, 0.3)'},
    'C': {'main': '#f59e0b', 'light': '#fef3c7', 'dark': '#92400e', 'glow': 'rgba(245, 158, 11, 0.3)'},
    'D': {'main': '#f97316', 'light': '#ffedd5', 'dark': '#9a3412', 'glow': 'rgba(249, 115, 22, 0.3)'},
    'F': {'main': '#ef4444', 'light': '#fee2e2', 'dark': '#991b1b', 'glow': 'rgba(239, 68, 68, 0.3)'}
}

# Line-art rat mark (original), monoline style. Inherits color via currentColor.
RAT_ICON_SVG = '''<svg width="96" height="54" viewBox="0 0 130 72" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" role="img" aria-label="rat icon">
<path d="M26 31 C13 31 10 17 20 14"/>
<path d="M111 57 L31 57 C18 57 11 46 16 36 C24 20 48 12 70 15 C86 17 96 26 99 35 L113 50 C116 53 115 57 111 57 Z"/>
<path d="M50 57 C42 51 42 41 50 36"/>
<circle cx="87" cy="24" r="10"/>
<circle cx="97" cy="40" r="3.5" fill="currentColor" stroke="none"/>
</svg>'''


def get_grade_color(grade: str, variant: str = 'main') -> str:
    """Get a grade color. Variants: main, light, dark, glow"""
    return GRADE_COLORS.get(grade, GRADE_COLORS['C'])[variant]


def get_base_styles() -> str:
    """Core CSS that should be included on every page."""
    return """
<style>
    /* ===== FONTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --font-body: 'Inter', -apple-system, 'Segoe UI', sans-serif;
        --font-display: 'Space Grotesk', sans-serif;

        /* Colors */
        --bg-primary: #ffffff;
        --bg-card: #ffffff;
        --bg-dark: #0a0a0a;
        --text-primary: #0a0a0a;
        --text-secondary: #525252;
        --text-muted: #a3a3a3;
        --border-hairline: #e7e7e7;
        --border-strong: #0a0a0a;
        --accent: #ef4444;

        /* Grade colors */
        --grade-a: #10b981;
        --grade-b: #84cc16;
        --grade-c: #f59e0b;
        --grade-d: #f97316;
        --grade-f: #ef4444;

        /* Shadows */
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
        --shadow-card: 0 12px 32px rgba(0,0,0,0.07);

        /* Animation */
        --transition-fast: 150ms ease;
        --transition-base: 250ms ease;
    }

    /* ===== BASE ===== */
    html, body, [class*="css"] {
        font-family: var(--font-body) !important;
        background-color: var(--bg-primary);
        -webkit-font-smoothing: antialiased;
    }

    h1, h2, h3 {
        font-family: var(--font-display) !important;
        letter-spacing: -0.02em;
    }

    footer {visibility: hidden;}

    .main .block-container {
        max-width: 1200px;
        padding: 1rem 1.5rem 3rem 1.5rem;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: #0a0a0a;
        border-right: 1px solid #1f1f1f;
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: #fafafa;
    }

    [data-testid="stSidebar"] a {
        color: #fafafa !important;
        text-decoration: none;
        transition: var(--transition-fast);
    }

    [data-testid="stSidebar"] a:hover {
        color: #a3a3a3 !important;
    }

    /* Force sidebar nav labels to always be visible with light text */
    [data-testid="stSidebarNav"] {
        color: #fafafa !important;
    }

    [data-testid="stSidebarNav"] span {
        color: #fafafa !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stSidebarNav"] a {
        color: #fafafa !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebarNav"] a span {
        color: #fafafa !important;
    }

    [data-testid="stSidebarNav"] li {
        color: #fafafa !important;
        opacity: 1 !important;
    }

    [data-testid="stSidebarNav"] li span {
        color: #fafafa !important;
    }

    [data-testid="stSidebarNavItems"] span {
        color: #fafafa !important;
    }

    [data-testid="stSidebarNavLink"] span {
        color: #fafafa !important;
    }

    /* Sidebar headers and labels - but NOT form inputs */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #fafafa !important;
    }

    /* Keep sidebar form inputs readable (dark text on light bg) */
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] {
        color: #0a0a0a !important;
        background-color: #ffffff !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] * {
        color: #0a0a0a !important;
    }

    /* ===== HERO SECTION (black panel) ===== */
    .hero-container {
        background: var(--bg-dark);
        color: #ffffff;
        text-align: center;
        padding: 4rem 2rem 4.5rem 2rem;
        margin: 0.5rem 0 2.5rem 0;
        border-radius: 12px;
        position: relative;
    }

    .hero-icon {
        color: #ffffff;
        margin-bottom: 1.5rem;
    }

    .hero-icon svg {
        display: inline-block;
    }

    .hero-title {
        font-family: var(--font-display) !important;
        font-size: clamp(2.75rem, 7vw, 4.75rem);
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.05;
    }

    .hero-subtitle {
        font-family: var(--font-body) !important;
        font-size: 1.0625rem;
        color: #a3a3a3;
        margin: 1.25rem auto 0 auto;
        max-width: 600px;
        line-height: 1.6;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border: 1px solid rgba(255,255,255,0.35);
        color: #ffffff;
        background: transparent;
        padding: 0.45rem 1.1rem;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        margin-top: 1.75rem;
        border-radius: 999px;
    }

    /* ===== PAGE HEADER ===== */
    .page-header {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        margin-bottom: 1rem;
    }

    .page-overline {
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: var(--text-muted);
        margin: 0 0 0.875rem 0;
    }

    .page-title {
        font-family: var(--font-display) !important;
        font-size: clamp(2rem, 5vw, 3rem);
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }

    .page-subtitle {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        margin: 0.875rem 0 0 0;
    }

    /* ===== SECTION LABELS ===== */
    .section-label {
        display: flex;
        align-items: center;
        gap: 0.875rem;
        margin: 2.25rem 0 1rem 0;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        color: var(--text-secondary);
    }

    .section-label::before {
        content: "";
        width: 8px;
        height: 8px;
        background: var(--bg-dark);
        flex: 0 0 auto;
    }

    .section-label::after {
        content: "";
        flex: 1;
        height: 1px;
        background: var(--border-hairline);
    }

    /* ===== CARDS ===== */
    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-hairline);
        border-radius: 10px;
        margin: 1.25rem 0;
        transition: var(--transition-base);
        position: relative;
        overflow: hidden;
    }

    .card:hover {
        box-shadow: var(--shadow-card);
        border-color: #d4d4d4;
        transform: translateY(-2px);
    }

    .card-header {
        background: var(--bg-card);
        color: var(--text-secondary);
        padding: 0.9rem 1.4rem;
        font-size: 0.6875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        border-bottom: 1px solid var(--border-hairline);
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }

    .card-header::before {
        content: "";
        width: 8px;
        height: 8px;
        background: var(--bg-dark);
        flex: 0 0 auto;
    }

    .card-header-icon {
        font-size: 1rem;
    }

    .card-body {
        padding: 1.5rem;
        background: var(--bg-card);
    }

    /* Static card variant (no hover effect) */
    .card-static {
        background: var(--bg-card);
        border: 1px solid var(--border-hairline);
        border-radius: 10px;
        margin: 1.25rem 0;
        overflow: hidden;
    }

    .card-static .card-body {
        padding: 1.5rem;
    }

    /* ===== STAT BOXES ===== */
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
    }

    .stat-box {
        text-align: center;
        padding: 1.5rem 1rem;
        background: var(--bg-card);
        border: 1px solid var(--border-hairline);
        border-radius: 8px;
        transition: var(--transition-fast);
    }

    .stat-box:hover {
        border-color: var(--border-strong);
    }

    .stat-value {
        font-family: var(--font-display) !important;
        font-size: 1.9rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }

    .stat-value-lg {
        font-size: 2.4rem;
    }

    .stat-label {
        font-size: 0.6875rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        line-height: 1.5;
        font-weight: 500;
    }

    .stat-delta {
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }

    .stat-delta.positive { color: var(--grade-a); }
    .stat-delta.negative { color: var(--grade-f); }

    /* Ghost numerals (White Label style 01 / 02 / 03) */
    .ghost-number {
        font-family: var(--font-display) !important;
        font-size: 2.25rem;
        font-weight: 700;
        color: #d4d4d4;
        line-height: 1;
        letter-spacing: -0.02em;
    }

    /* ===== GRADE BADGES ===== */
    .grade-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        font-family: var(--font-display) !important;
        font-size: 1.25rem;
        font-weight: 700;
        border-radius: 6px;
        color: white;
    }

    .grade-badge-lg {
        width: 5rem;
        height: 5rem;
        font-size: 3rem;
        border-radius: 10px;
    }

    .grade-badge-xl {
        width: 8rem;
        height: 8rem;
        font-size: 5rem;
        border-radius: 14px;
        box-shadow: var(--shadow-card);
    }

    .grade-a { background: var(--grade-a); }
    .grade-b { background: var(--grade-b); }
    .grade-c { background: var(--grade-c); }
    .grade-d { background: var(--grade-d); }
    .grade-f { background: var(--grade-f); }

    /* Grade with glow effect */
    .grade-badge-glow {
        animation: pulse-glow 2s ease-in-out infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px var(--glow-color, rgba(0,0,0,0.2)); }
        50% { box-shadow: 0 0 40px var(--glow-color, rgba(0,0,0,0.3)); }
    }

    /* ===== GRADE DISPLAY (large centered grade) ===== */
    .grade-display {
        text-align: center;
        padding: 2rem;
    }

    .grade-letter {
        font-family: var(--font-display) !important;
        font-size: clamp(6rem, 20vw, 10rem);
        font-weight: 700;
        line-height: 1;
        margin: 0;
    }

    .grade-ward {
        font-family: var(--font-display) !important;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 1.5rem 0 0.5rem 0;
    }

    .grade-desc {
        font-size: 1rem;
        color: var(--text-secondary);
        margin: 0;
    }

    /* ===== DATA TABLES ===== */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border-hairline) !important;
        border-radius: 8px !important;
        overflow: hidden;
    }

    div[data-testid="stDataFrame"] table {
        font-family: var(--font-body) !important;
    }

    /* ===== FOOTER ===== */
    .site-footer {
        text-align: center;
        padding: 2.5rem 1rem 1rem 1rem;
        color: var(--text-muted);
        font-size: 0.75rem;
        border-top: 1px solid var(--border-hairline);
        margin-top: 3.5rem;
    }

    .site-footer a {
        color: var(--text-primary);
        text-decoration: none;
        transition: var(--transition-fast);
    }

    .site-footer a:hover {
        color: var(--text-muted);
    }

    /* ===== LIVE INDICATOR ===== */
    .live-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: var(--grade-a);
        border-radius: 50%;
        animation: live-pulse 2s ease-in-out infinite;
    }

    @keyframes live-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }

    /* ===== RANK BADGE ===== */
    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 2rem;
        height: 1.5rem;
        padding: 0 0.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 4px;
        color: white;
    }

    .rank-top { background: var(--grade-a); }
    .rank-mid { background: var(--grade-c); }
    .rank-low { background: var(--grade-f); }

    /* ===== PROGRESS BAR ===== */
    .progress-container {
        background: #ececec;
        border-radius: 999px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .progress-bar {
        height: 100%;
        background: var(--bg-dark);
        transition: width 0.5s ease;
    }

    /* ===== RESPONSIVE GRID CLASSES ===== */
    .stats-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
    }

    .stats-grid-5 {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1rem;
    }

    .stats-grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
        .hero-container {
            padding: 3rem 1.25rem 3.5rem 1.25rem;
            border-radius: 10px;
        }

        .stat-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .stats-grid-4 {
            grid-template-columns: repeat(2, 1fr);
        }

        .stats-grid-5 {
            grid-template-columns: repeat(3, 1fr);
        }

        .stats-grid-3 {
            grid-template-columns: repeat(2, 1fr);
        }

        .card-body {
            padding: 1rem;
        }
    }

    @media (max-width: 480px) {
        .hero-title {
            font-size: 2.25rem;
        }

        .hero-subtitle {
            font-size: 0.9375rem;
        }

        .stats-grid-4 {
            grid-template-columns: 1fr;
        }

        .stats-grid-5 {
            grid-template-columns: repeat(2, 1fr);
        }

        .stats-grid-3 {
            grid-template-columns: 1fr;
        }

        .stat-value {
            font-size: 1.5rem;
        }

        .card-body {
            padding: 0.875rem;
        }

        .page-header {
            padding: 1.75rem 0.5rem 1rem 0.5rem;
        }
    }

    /* ===== UTILITIES ===== */
    .text-center { text-align: center; }
    .text-display { font-family: var(--font-display) !important; }
    .text-muted { color: var(--text-muted); }
    .text-sm { font-size: 0.875rem; }
    .text-xs { font-size: 0.75rem; }
    .mt-1 { margin-top: 0.5rem; }
    .mt-2 { margin-top: 1rem; }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }

</style>
"""


def render_card(header: str, body_html: str, icon: str = None, static: bool = False) -> str:
    """Render a styled card with header and body."""
    card_class = "card-static" if static else "card"
    icon_html = f'<span class="card-header-icon">{icon}</span>' if icon else ''
    return f"""
    <div class="{card_class}">
        <div class="card-header">{icon_html}{header}</div>
        <div class="card-body">{body_html}</div>
    </div>
    """


def render_stat_box(value: str, label: str, delta: str = None, delta_type: str = None) -> str:
    """Render a single stat box."""
    delta_html = ""
    if delta:
        delta_class = delta_type if delta_type in ['positive', 'negative'] else ''
        delta_html = f'<p class="stat-delta {delta_class}">{delta}</p>'

    return f"""
    <div class="stat-box">
        <p class="stat-value">{value}</p>
        <p class="stat-label">{label}</p>
        {delta_html}
    </div>
    """


def render_grade_badge(grade: str, size: str = 'md') -> str:
    """Render a grade badge. Sizes: sm, md, lg, xl"""
    size_class = {
        'sm': '',
        'md': '',
        'lg': 'grade-badge-lg',
        'xl': 'grade-badge-xl'
    }.get(size, '')

    return f'<span class="grade-badge {size_class} grade-{grade.lower()}">{grade}</span>'


def render_hero(title: str, subtitle: str = None, badge: str = None) -> str:
    """Render the hero section (black panel with line-art rat mark)."""
    subtitle_html = f'<p class="hero-subtitle">{subtitle}</p>' if subtitle else ''
    badge_html = f'<span class="hero-badge"><span class="live-dot"></span>{badge}</span>' if badge else ''

    return f"""
    <div class="hero-container">
        <div class="hero-icon">{RAT_ICON_SVG}</div>
        <h1 class="hero-title">{title}</h1>
        {subtitle_html}
        {badge_html}
    </div>
    """


def render_page_header(title: str, subtitle: str = None) -> str:
    """Render a page header (smaller than hero) with brand overline."""
    subtitle_html = f'<p class="page-subtitle">{subtitle}</p>' if subtitle else ''

    return f"""
    <div class="page-header">
        <p class="page-overline">Where the Rats At?</p>
        <h1 class="page-title">{title}</h1>
        {subtitle_html}
    </div>
    """


def render_section_label(text: str) -> str:
    """Render a minimal uppercase section label with a hairline rule."""
    return f'<p class="section-label"><span>{text}</span></p>'


def render_footer(data_date: str = None) -> str:
    """Render the site footer."""
    date_text = f"Most recent: {data_date}" if data_date else "Updated hourly"

    return f"""
    <div class="site-footer">
        <p>
            <span class="live-indicator"><span class="live-dot"></span> Live data</span>
            &nbsp;&middot;&nbsp;
            <a href="https://data.cityofchicago.org">Chicago Data Portal</a>
            &nbsp;&middot;&nbsp;
            {date_text}
        </p>
        <p style="margin-top: 1rem;">
            &copy; 2025 <a href="https://www.linkedin.com/in/seanwmcguire/">Sean W. McGuire</a>
        </p>
    </div>
    """


def render_live_indicator() -> str:
    """Render a live data indicator."""
    return '<span class="live-indicator"><span class="live-dot"></span> Live</span>'


def get_rank_class(rank: int, total: int = 50) -> str:
    """Get CSS class for rank badge based on position."""
    pct = rank / total
    if pct <= 0.2:
        return 'rank-top'
    elif pct <= 0.6:
        return 'rank-mid'
    else:
        return 'rank-low'
