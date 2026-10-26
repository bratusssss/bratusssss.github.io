"""Ģenerē ploteris.lv lapas no viena avota.

Palaišana (no repozitorija saknes):  python3 _src/build.py
Jekyll neizvieto mapes, kuru nosaukums sākas ar "_", tāpēc šis fails netiek publicēts.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ploteris.lv"
TODAY = date.today().isoformat()

PHONE1, PHONE1_TEL = "+371 26 325 307", "+37126325307"
PHONE2, PHONE2_TEL = "+371 24 424 434", "+37124424434"
EMAIL = "sales@bratus.lv"
BUY_URL = "https://bratus.lv/products/plotergriezejs"

MODELS = [
    {
        "slug": "ploteris-71-cm", "cm": "71", "price": "544.50", "price_lv": "544,50",
        "short": "Kompakts ploteris mājamatniecībai, papīra un vinila griešanai ierobežotos formātos.",
        "for": "mājamatniecībai, papīra un vinila griešanai ierobežotos formātos",
    },
    {
        "slug": "ploteris-86-cm", "cm": "86", "price": "641.30", "price_lv": "641,30",
        "short": "Vidējā izmēra ploteris ikdienas darbam dizaina studijā un T-kreklu apdrukai ar termoplēvi.",
        "for": "ikdienas darbam dizaina studijā un T-kreklu apdrukai ar termoplēvi",
    },
    {
        "slug": "ploteris-134-cm", "cm": "134", "price": "822.80", "price_lv": "822,80",
        "short": "Lielformāta ploteris auto uzlīmēm un lieliem baneriem.",
        "for": "auto uzlīmēm un lieliem baneriem",
    },
]

NAV = [
    ("/", "Sākums"),
    ("/#modeli", "Modeļi"),
    ("/cenas/", "Cenas"),
    ("/uzlimju-ploteris/", "Pielietojums"),
    ("/kas-ir-ploteris/", "Kas ir ploteris"),
    ("/kontakti/", "Kontakti"),
]

ORG = {
    "@type": "Organization",
    "@id": f"{SITE}/#org",
    "name": "SIA Bratus",
    "url": "https://bratus.lv",
    "logo": f"{SITE}/assets/img/favicon.png",
    "email": EMAIL,
    "telephone": PHONE1_TEL,
    "vatID": "LV40203628316",
    "taxID": "40203628316",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Pliederu iela 22",
        "addressLocality": "Ķekava",
        "addressRegion": "Ķekavas novads",
        "addressCountry": "LV",
    },
    "contactPoint": [
        {"@type": "ContactPoint", "telephone": PHONE1_TEL, "contactType": "sales", "areaServed": "LV", "availableLanguage": "lv"},
        {"@type": "ContactPoint", "telephone": PHONE2_TEL, "contactType": "sales", "areaServed": "LV", "availableLanguage": "lv"},
    ],
}
WEBSITE = {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Ploteris.lv", "inLanguage": "lv", "publisher": {"@id": f"{SITE}/#org"}}


# ─────────────────────────── Kopīgās daļas ───────────────────────────

def breadcrumbs_html(trail):
    items = "".join(
        f'<li><a href="{url}">{name}</a></li>' if url else f'<li aria-current="page">{name}</li>'
        for name, url in trail
    )
    return f'<nav class="breadcrumbs wrap" aria-label="Ceļa norāde"><ol>{items}</ol></nav>'


def breadcrumbs_ld(trail, path):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + (url or path)}
            for i, (name, url) in enumerate(trail)
        ],
    }


def faq_html(items):
    return '<div class="faq">' + "".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items
    ) + "</div>"


def faq_ld(items):
    import re
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
            for q, a in items
        ],
    }


def product_ld(m):
    url = f"{SITE}/{m['slug']}/"
    return {
        "@type": "Product",
        "@id": url + "#product",
        "name": f"Griešanas ploteris {m['cm']} cm",
        "description": m["short"],
        "image": [f"{SITE}/assets/img/griesanas-ploteris-stativa.webp", f"{SITE}/assets/img/plotera-griesanas-galvina.webp"],
        "category": "Griešanas ploteri",
        "offers": {
            "@type": "Offer",
            "url": url,
            "price": m["price"],
            "priceCurrency": "EUR",
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": m["price"], "priceCurrency": "EUR", "valueAddedTaxIncluded": False},
            "itemCondition": "https://schema.org/NewCondition",
            "seller": {"@id": f"{SITE}/#org"},
        },
    }


CTA_BAND = f"""
<section class="cta-band">
  <div class="wrap">
    <h2>Neesat pārliecināts, kurš platums Jums der?</h2>
    <p>Pastāstiet, ko plānojat griezt un kādā izmērā. Mēs ieteiksim piemērotāko modeli un atbildēsim uz jautājumiem par pasūtīšanu.</p>
    <div class="btn-row">
      <a class="btn btn-primary" href="tel:{PHONE1_TEL}">Zvanīt {PHONE1}</a>
      <a class="btn btn-ghost" href="/kontakti/">Rakstīt mums</a>
    </div>
  </div>
</section>"""


def page(path, title, description, body, ld=None, og_type="website", nav_key=None):
    canonical = SITE + path
    # Nedalāma atstarpe starp skaitli un mērvienību, lai „134 cm” nepārlūzt rindā
    body = re.sub(r"(\d) (cm|mm|g|€|mēn)(?=[\s.,;:<)–]|$)", "\\1&nbsp;\\2", body)
    graph = [ORG, WEBSITE] + (ld or [])
    ld_json = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    nav_html = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == nav_key else ""}>{name}</a>' for href, name in NAV
    )
    model_links = "".join(f'<li><a href="/{m["slug"]}/">Ploteris {m["cm"]} cm</a></li>' for m in MODELS)
    html = f"""<!DOCTYPE html>
<html lang="lv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="google-site-verification" content="ONSL5wxpzUSRXozoKSlH7bPaYvHTLznGXY1R0U0ym1U">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="lv" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="lv_LV">
<meta property="og:site_name" content="Ploteris.lv">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/img/og-ploteris.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta name="theme-color" content="#fffbf5">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>
<a class="skip" href="#saturs">Pāriet uz saturu</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="Ploteris.lv – sākumlapa">
      <img src="/assets/img/logo.png" alt="" width="19" height="26">
      <span>Ploteris<em>.lv</em></span>
    </a>
    <nav class="main-nav" id="main-nav" aria-label="Galvenā izvēlne">{nav_html}</nav>
    <div class="header-cta">
      <a class="btn btn-primary btn-small" href="tel:{PHONE1_TEL}">{PHONE1}</a>
      <button class="menu-btn" id="menu-btn" aria-controls="main-nav" aria-expanded="false">Izvēlne</button>
    </div>
  </div>
</header>
<main id="saturs">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>Ploteris.lv</h2>
        <p>Griešanas ploteru pārdošana Latvijā. Lapu uztur SIA Bratus, kas pārdod CNC iekārtas, nodrošina to apkopi un remontu.</p>
      </div>
      <div>
        <h2>Ploteri</h2>
        <ul>{model_links}<li><a href="/cenas/">Cenas</a></li></ul>
      </div>
      <div>
        <h2>Informācija</h2>
        <ul>
          <li><a href="/kas-ir-ploteris/">Kas ir ploteris</a></li>
          <li><a href="/uzlimju-ploteris/">Pielietojums</a></li>
          <li><a href="/kontakti/">Kontakti</a></li>
          <li><a href="https://bratus.lv">Citas iekārtas bratus.lv</a></li>
        </ul>
      </div>
      <div>
        <h2>Kontakti</h2>
        <ul>
          <li><a href="tel:{PHONE1_TEL}">{PHONE1}</a></li>
          <li><a href="tel:{PHONE2_TEL}">{PHONE2}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>Pliederu iela 22, Ķekava, Ķekavas nov.</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">© <span id="yr">2026</span> SIA Bratus · Reģ. nr. 40203628316</div>
  </div>
</footer>
<script src="/assets/main.js" defer></script>
</body>
</html>
"""
    out = ROOT / path.strip("/") / "index.html" if path != "/404.html" else ROOT / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return path


# ─────────────────────────── Saturs ───────────────────────────

def model_cards():
    cards = ""
    for m in MODELS:
        cards += f"""
      <article class="card">
        <h3><a href="/{m['slug']}/">Ploteris {m['cm']} cm</a></h3>
        <p>{m['short']}</p>
        <ul>
          <li>{m['cm']} cm darba platums</li>
          <li>Komplektā programmatūra</li>
          <li>18 mēnešu garantija</li>
        </ul>
        <div class="card-spacer"></div>
        <div class="price">{m['price_lv']} €<small>bez PVN</small></div>
        <a class="btn btn-ghost btn-small" href="/{m['slug']}/">Skatīt {m['cm']} cm modeli</a>
      </article>"""
    return f'<div class="cards">{cards}\n    </div>'


MATERIALS_TABLE = """
<div class="table-wrap">
  <table>
    <thead><tr><th scope="col">Materiāls</th><th scope="col">Piezīmes</th></tr></thead>
    <tbody>
      <tr><td>Vinila plēve (ploterplēve)</td><td>Standarta pielietojums: uzlīmes, uzraksti, logo</td></tr>
      <tr><td>Termoplēve (HTV, Flex plēve)</td><td>T-kreklu un tekstila apdruka</td></tr>
      <tr><td>Flokētā plēve (floks)</td><td>Samtaina virsma tekstilam</td></tr>
      <tr><td>Papīrs un amatniecības papīrs</td><td>Līdz vidējam biezumam</td></tr>
      <tr><td>Kartons</td><td>Plānāki kartona veidi</td></tr>
      <tr><td>Krāsu maskas</td><td>Lietošanai ar lāzergravētājiem</td></tr>
    </tbody>
  </table>
</div>"""

HOME_FAQ = [
    ("Cik maksā griešanas ploteris?",
     'Plotergriezēja 71 cm modelis maksā 544,50 €, 86 cm modelis – 641,30 €, bet 134 cm modelis – 822,80 €. Visas cenas norādītas bez PVN. Salīdzinājums ir lapā <a href="/cenas/">Cenas</a>.'),
    ("Kādus materiālus var griezt ar ploteri?",
     "Vinila plēvi, termoplēvi (HTV jeb Flex plēvi), flokēto plēvi, papīru līdz vidējam biezumam, plānākus kartona veidus un krāsu maskas lāzergravēšanai."),
    ("Kāda programmatūra ir vajadzīga?",
     "Programmatūra failu sagatavošanai ir iekļauta komplektā. Ploteris saprot DM/PL un HP/GL komandvalodas un ir saderīgs ar Windows XP, Vista, 7, 8 un 10."),
    ("Vai ploteris darbojas ar Mac datoru?",
     "Nē. Saskaņā ar tehnisko specifikāciju Mac netiek atbalstīts, tāpēc ploterim vajadzīgs dators ar Windows."),
    ("Kā ploteri pievieno datoram?",
     "Ar USB kabeli vai caur COM (RS-232) pieslēgvietu. USB kabelis ir komplektā."),
    ("Kāda ir garantija?",
     "Visiem trim modeļiem garantija ir 18 mēneši."),
    ("Kā iegādāties ploteri?",
     f'Zvaniet <a href="tel:{PHONE1_TEL}">{PHONE1}</a>, rakstiet uz <a href="mailto:{EMAIL}">{EMAIL}</a> vai pasūtiet internetā <a href="{BUY_URL}">bratus.lv</a>.'),
]


def build_home():
    body = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Plotergriezēji · SIA Bratus</span>
      <h1>Griešanas ploteris vinilam, termoplēvei un kartonam</h1>
      <p class="lead">Pārdodam plotergriezējus 71, 86 un 134 cm platumā. Griešanas spiedienu var regulēt no 10 līdz 500 g, ātrumu – līdz 800 mm/s, un katram modelim ir 18 mēnešu garantija.</p>
      <div class="btn-row">
        <a class="btn btn-primary" href="#modeli">Skatīt modeļus un cenas</a>
        <a class="btn btn-ghost" href="tel:{PHONE1_TEL}">Zvanīt {PHONE1}</a>
      </div>
    </div>
    <div class="hero-img">
      <img src="/assets/img/griesanas-ploteris-stativa.webp" width="1400" height="953" alt="Griešanas ploteris uz metāla statīva ar ruļļa turētāju" fetchpriority="high">
    </div>
  </div>
</section>

<div class="wrap">
  <div class="stats">
    <div class="stat"><b>71 · 86 · 134 cm</b><span>Trīs darba platumi</span></div>
    <div class="stat"><b>10–500 g</b><span>Griešanas spiediens</span></div>
    <div class="stat"><b>800 mm/s</b><span>Maksimālais ātrums</span></div>
    <div class="stat"><b>18 mēn.</b><span>Garantija</span></div>
  </div>
</div>

<section class="section" id="kas-ir">
  <div class="wrap two-col">
    <div class="prose">
      <h2>Kas ir griešanas ploteris</h2>
      <p>Griešanas ploteris jeb plotergriezējs ar asmeni izgriež kontūras no plēves, papīra vai kartona pēc datorā sagatavota faila. Ar to izgatavo uzlīmes, uzrakstus uz skatlogiem un automašīnām, kā arī termoplēves attēlus apģērbam.</p>
      <p>Griešanas ploteris nedrukā. Ja meklējat iekārtu rasējumu vai plakātu drukāšanai, Jums vajadzīgs drukas ploteris, piemēram, HP DesignJet. Atšķirību sīkāk skaidrojam lapā <a href="/kas-ir-ploteris/">Kas ir ploteris</a>.</p>
    </div>
    <figure class="hero-img">
      <img src="/assets/img/plotera-griesanas-galvina.webp" width="1400" height="667" alt="Plotera griešanas galviņa ar asmeni un LCD vadības paneli" loading="lazy">
    </figure>
  </div>
</section>

<section class="section section-alt" id="modeli">
  <div class="wrap">
    <div class="section-head">
      <h2>Plotergriezēju modeļi un cenas</h2>
      <p>Modeļi atšķiras ar darba platumu. Izvēlieties to pēc platākā materiāla, ko plānojat griezt. Cenas norādītas bez PVN.</p>
    </div>
    {model_cards()}
  </div>
</section>

<section class="section" id="materiali">
  <div class="wrap two-col">
    <div class="prose">
      <h2>Ko var griezt ar ploteri</h2>
      <p>Spiedienu un ātrumu iestata tieši plotera panelī. Plānam papīram vajag mazu spiedienu, bet biezākai plēvei – lielāku. Tā vienu iekārtu var izmantot dažādiem materiāliem.</p>
      <p>Piemērus un modeļu izvēli pēc darba veida aprakstām lapā <a href="/uzlimju-ploteris/">Ploteris uzlīmēm un termoplēvei</a>.</p>
    </div>
    {MATERIALS_TABLE}
  </div>
</section>

<section class="section section-alt" id="tehniskie-dati">
  <div class="wrap">
    <div class="section-head">
      <h2>Tehniskie dati</h2>
      <p>Šie parametri attiecas uz plotergriezējiem, ko piedāvājam. Pilnu tabulu katram modelim atradīsiet modeļa lapā.</p>
    </div>
    <div class="features">
      <div class="feature">
        <h3>Griešanas spiediens 10–500 g</h3>
        <p>Spiedienu regulē atbilstoši materiālam. Asmens pozicionēšanas precizitāte ir 0,01 mm.</p>
      </div>
      <div class="feature">
        <h3>Ātrums līdz 800 mm/s</h3>
        <p>Griešanas ātrums ir regulējams no 10 līdz 800 mm/s, un to var mainīt tieši vadības panelī.</p>
      </div>
      <div class="feature">
        <h3>Alumīnija korpuss un rullīši</h3>
        <p>Korpuss ir no biezināta alumīnija. Materiālu padod dubultā alumīnija rullīšu sistēma ar atsperu piespiedējrullīšiem.</p>
      </div>
      <div class="feature">
        <h3>USB un COM pieslēgums</h3>
        <p>Ploteris saprot DM/PL un HP/GL komandvalodas un darbojas ar Windows XP, Vista, 7, 8 un 10. Mac netiek atbalstīts.</p>
      </div>
    </div>
    <div class="gallery">
      <figure><img src="/assets/img/plotera-vadibas-panelis.webp" width="750" height="392" alt="Plotera LCD vadības panelis ar pogām Reset, Leave, Setting, Test un Origin" loading="lazy"><figcaption>LCD vadības panelis</figcaption></figure>
      <figure><img src="/assets/img/plotera-usb-com-pieslegumi.webp" width="550" height="366" alt="Plotera USB un COM pieslēgvietas" loading="lazy"><figcaption>USB un COM pieslēgvietas</figcaption></figure>
    </div>
  </div>
</section>

<section class="section" id="komplektacija">
  <div class="wrap two-col">
    <div class="prose">
      <h2>Komplektācija un garantija</h2>
      <ul>
        <li>Ploteris</li>
        <li>Programmatūra failu sagatavošanai</li>
        <li>Barošanas kabelis</li>
        <li>USB kabelis</li>
      </ul>
      <p>Garantija ir 18 mēneši. Iekļauta apmācība un uzstādīšanas demonstrācija. SIA Bratus nodrošina CNC iekārtu apkopi un remontu.</p>
    </div>
    <div class="prose">
      <h2>Kam ploteris neder</h2>
      <p>Ploteris nav piemērots, ja Jūs strādājat tikai ar Mac datoru, jo Mac netiek atbalstīts. Biezu kartonu tas negriež: kartonam der plānāki veidi, papīram – līdz vidējam biezumam.</p>
      <p>Ja nepieciešams griezt vai gravēt koku, akrilu vai biezu kartonu, apskatiet CO2 lāzerus un CNC frēzes vietnē <a href="https://bratus.lv">bratus.lv</a>.</p>
    </div>
  </div>
</section>

<section class="section section-alt" id="buj">
  <div class="wrap">
    <h2>Biežāk uzdotie jautājumi</h2>
    {faq_html(HOME_FAQ)}
  </div>
</section>
{CTA_BAND}"""
    page("/", "Griešanas ploteris (plotergriezējs) 71, 86, 134 cm | Ploteris.lv",
         "Griešanas ploteri vinilam, termoplēvei un kartonam: 71, 86 un 134 cm platumā, spiediens 10–500 g, 18 mēnešu garantija. Cena no 544,50 € bez PVN.",
         body, ld=[faq_ld(HOME_FAQ), {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{m['slug']}/"} for i, m in enumerate(MODELS)]}],
         nav_key="/")


def spec_rows(m):
    rows = [("Darba platums", f"{m['cm']} cm")]
    if m["cm"] == "134":
        rows += [
            ("Maksimālais materiāla platums", "1350 mm"),
            ("Maksimālais griešanas platums", "1260 mm"),
            ("Griešanas garums", "Neierobežots (ruļļa materiāls)"),
        ]
    rows += [
        ("Griešanas spiediens", "10–500 g, regulējams"),
        ("Griešanas ātrums", "10–800 mm/s, regulējams"),
        ("Asmens pozicionēšanas precizitāte", "0,01 mm"),
    ]
    if m["cm"] == "134":
        rows += [
            ("Atkārtojamības precizitāte", "≤ 0,01 mm"),
            ("Griešanas dziļuma regulēšana", "Mehāniska"),
            ("Motori", "Soļu motori"),
        ]
    rows += [
        ("Rullīšu sistēma", "Dubultā alumīnija rullīšu sistēma ar atsperu piespiedējrullīšiem" if m["cm"] == "134" else "Dubultā rullīšu sistēma"),
        ("Korpuss", "Biezināts alumīnijs" if m["cm"] == "134" else "Alumīnijs"),
        ("Vadības panelis", "LCD displejs ar pogām"),
        ("Pieslēgumi", "USB, COM (RS-232)"),
        ("Komandvalodas", "DM/PL, HP/GL"),
        ("Operētājsistēmas", "Windows XP, Vista, 7, 8, 10"),
        ("Mac saderība", "Nav"),
        ("Garantija", "18 mēneši"),
    ]
    return "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)


def build_model(m):
    others = " ".join(
        f'<a class="btn btn-ghost btn-small" href="/{o["slug"]}/">Ploteris {o["cm"]} cm – {o["price_lv"]} €</a>'
        for o in MODELS if o is not m
    )
    intro = {
        "71": "Šis ir mazākais no mūsu plotergriezējiem. Tas der mājamatniecībai, kā arī papīra un vinila griešanai ierobežotos formātos, kad nav vajadzīgs plats materiāls.",
        "86": "Vidējais modelis der ikdienas darbam dizaina studijā. Ar to var griezt vinila plēvi uzlīmēm un termoplēvi T-kreklu un tekstila apdrukai.",
        "134": "Lielākais no mūsu plotergriezējiem. Tas paredzēts lielformāta darbiem – auto uzlīmēm un lieliem baneriem. Materiāla padeves platums ir līdz 1350 mm, griešanas platums – līdz 1260 mm, bet garums ruļļa materiālam nav ierobežots.",
    }[m["cm"]]
    path = f"/{m['slug']}/"
    trail = [("Sākums", "/"), ("Modeļi", "/#modeli"), (f"Ploteris {m['cm']} cm", None)]
    body = f"""
{breadcrumbs_html(trail)}
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Plotergriezējs · {m['cm']} cm</span>
      <h1>Griešanas ploteris {m['cm']} cm</h1>
      <p class="lead">{intro}</p>
    </div>
    <div class="buy-box">
      <div class="price">{m['price_lv']} € <small>bez PVN</small></div>
      <ul>
        <li>{m['cm']} cm darba platums</li>
        <li>Komplektā programmatūra, barošanas un USB kabelis</li>
        <li>18 mēnešu garantija</li>
        <li>Apmācība un uzstādīšanas demonstrācija</li>
      </ul>
      <div class="btn-row">
        <a class="btn btn-primary" href="{BUY_URL}">Pasūtīt bratus.lv</a>
        <a class="btn btn-ghost" href="tel:{PHONE1_TEL}">Zvanīt {PHONE1}</a>
      </div>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap two-col">
    <div>
      <h2>Tehniskie dati</h2>
      <div class="table-wrap"><table><tbody>{spec_rows(m)}</tbody></table></div>
    </div>
    <div class="prose">
      <h2>Kam šis modelis der</h2>
      <p>Ploteris {m['cm']} cm ir paredzēts {m['for']}.</p>
      <p>Ar to var griezt vinila plēvi, termoplēvi, flokēto plēvi, papīru līdz vidējam biezumam, plānākus kartona veidus un krāsu maskas lāzergravēšanai. Plašāk par materiāliem – lapā <a href="/uzlimju-ploteris/">Pielietojums</a>.</p>
      <h3>Kas jāņem vērā</h3>
      <p>Ploterim vajadzīgs dators ar Windows, jo Mac netiek atbalstīts. Biezu kartonu ploteris negriež.</p>
      <figure class="hero-img" style="margin-top:20px">
        <img src="/assets/img/plotera-griesanas-galvina.webp" width="1400" height="667" alt="Plotergriezēja {m['cm']} cm griešanas galviņa un vadības panelis" loading="lazy">
      </figure>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <h2>Citi modeļi</h2>
    <p>Modeļi atšķiras ar darba platumu un cenu. Visu modeļu salīdzinājums ir lapā <a href="/cenas/">Cenas</a>.</p>
    <div class="btn-row">{others}</div>
  </div>
</section>
{CTA_BAND}"""
    page(path, f"Ploteris {m['cm']} cm – griešanas ploteris, {m['price_lv']} € bez PVN | Ploteris.lv",
         f"Griešanas ploteris {m['cm']} cm {m['for']}. Spiediens 10–500 g, 18 mēnešu garantija. Cena {m['price_lv']} € bez PVN.",
         body, ld=[product_ld(m), breadcrumbs_ld(trail, path)], og_type="product", nav_key="/#modeli")


PRICE_FAQ = [
    ("Vai cenās ir iekļauts PVN?", "Nē. Visas cenas šajā lapā norādītas bez PVN."),
    ("Kas ir iekļauts cenā?", "Ploteris, programmatūra failu sagatavošanai, barošanas kabelis un USB kabelis. Iekļauta arī apmācība un uzstādīšanas demonstrācija."),
    ("Kāda ir garantija?", "Visiem trim modeļiem garantija ir 18 mēneši."),
    ("Kā uzzināt piegādes un apmaksas nosacījumus?",
     f'Zvaniet <a href="tel:{PHONE1_TEL}">{PHONE1}</a> vai rakstiet uz <a href="mailto:{EMAIL}">{EMAIL}</a>.'),
]


def build_prices():
    rows = "".join(
        f'<tr><td><a href="/{m["slug"]}/">Ploteris {m["cm"]} cm</a></td><td>{m["cm"]} cm</td><td>{m["for"][0].upper() + m["for"][1:]}</td><td class="num"><b>{m["price_lv"]} €</b></td></tr>'
        for m in MODELS
    )
    trail = [("Sākums", "/"), ("Cenas", None)]
    body = f"""
{breadcrumbs_html(trail)}
<section class="hero">
  <div class="wrap">
    <span class="eyebrow">Ploteris cena</span>
    <h1>Plotergriezēju cenas</h1>
    <p class="lead">Griešanas ploteris maksā no 544,50 € līdz 822,80 € bez PVN. Cena atkarīga no darba platuma, bet komplektācija un garantija visiem modeļiem ir vienāda.</p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <div class="table-wrap">
      <table>
        <thead><tr><th scope="col">Modelis</th><th scope="col">Darba platums</th><th scope="col">Kam domāts</th><th scope="col">Cena bez PVN</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
    <div class="btn-row">
      <a class="btn btn-primary" href="{BUY_URL}">Pasūtīt bratus.lv</a>
      <a class="btn btn-ghost" href="/kontakti/">Pieprasīt piedāvājumu</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap two-col">
    <div class="prose">
      <h2>Kas iekļauts cenā</h2>
      <ul>
        <li>Ploteris</li>
        <li>Programmatūra failu sagatavošanai</li>
        <li>Barošanas kabelis un USB kabelis</li>
        <li>Apmācība un uzstādīšanas demonstrācija</li>
        <li>18 mēnešu garantija</li>
      </ul>
    </div>
    <div class="prose">
      <h2>Kā izvēlēties platumu</h2>
      <p>Darba platumu izvēlieties pēc platākā materiāla vai darba, ko plānojat griezt. 71 cm modelis der mājamatniecībai un nelieliem formātiem, 86 cm – ikdienas darbam dizaina studijā, bet 134 cm – auto uzlīmēm un lieliem baneriem.</p>
      <p>Ja šaubāties, aprakstiet savu darbu, un mēs ieteiksim piemērotāko modeli.</p>
    </div>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap">
    <h2>Jautājumi par cenu</h2>
    {faq_html(PRICE_FAQ)}
  </div>
</section>
{CTA_BAND}"""
    offers = {
        "@type": "Product",
        "name": "Griešanas ploteris",
        "description": "Griešanas ploteri 71, 86 un 134 cm platumā.",
        "image": f"{SITE}/assets/img/griesanas-ploteris-stativa.webp",
        "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": "544.50", "highPrice": "822.80", "offerCount": 3},
    }
    page("/cenas/", "Ploteris cena – plotergriezēji no 544,50 € bez PVN | Ploteris.lv",
         "Griešanas plotera cena: 71 cm – 544,50 €, 86 cm – 641,30 €, 134 cm – 822,80 € bez PVN. Komplektā programmatūra un kabeļi, 18 mēnešu garantija.",
         body, ld=[offers, faq_ld(PRICE_FAQ), breadcrumbs_ld(trail, "/cenas/")], nav_key="/cenas/")


def build_guide():
    trail = [("Sākums", "/"), ("Kas ir ploteris", None)]
    body = f"""
{breadcrumbs_html(trail)}
<article>
<section class="hero">
  <div class="wrap">
    <span class="eyebrow">Ceļvedis</span>
    <h1>Kas ir ploteris un kā darbojas griešanas ploteris</h1>
    <p class="lead">Ar vārdu „ploteris” apzīmē divas dažādas iekārtas – drukas ploteri un griešanas ploteri. Šajā lapā skaidrojam atšķirību, griešanas plotera darbību un parametrus, kam pievērst uzmanību, izvēloties iekārtu.</p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap prose">
    <h2>Drukas ploteris un griešanas ploteris</h2>
    <p><strong>Drukas ploteris</strong> ir platformāta printeris. To izmanto rasējumu, karšu un plakātu drukāšanai uz papīra ruļļa, un pazīstams piemērs ir HP DesignJet sērija.</p>
    <p><strong>Griešanas ploteris</strong> jeb plotergriezējs nedrukā. Tas ar asmeni izgriež kontūras materiālā, piemēram, vinila plēvē, termoplēvē, papīrā vai plānā kartonā. Ploteris.lv piedāvā tikai griešanas ploterus.</p>

    <h2>Kā darbojas griešanas ploteris</h2>
    <ol>
      <li><strong>Fails.</strong> Datorā sagatavo vektora zīmējumu – tekstu, logo vai kontūru. Programmatūra failu sagatavošanai ir komplektā ar mūsu ploteriem.</li>
      <li><strong>Komandas.</strong> Programma nosūta ploterim komandas DM/PL vai HP/GL valodā caur USB vai COM pieslēgumu.</li>
      <li><strong>Griešana.</strong> Rullīši pārvieto materiālu turp un atpakaļ, bet griešanas galviņa ar asmeni pārvietojas sāniski. Tā asmens izgriež zīmējuma kontūru.</li>
      <li><strong>Spiediens un ātrums.</strong> Spiediens nosaka, cik dziļi asmens iegriež. Mūsu ploteriem to regulē no 10 līdz 500 g, bet ātrumu – no 10 līdz 800 mm/s.</li>
    </ol>
    <figure class="hero-img" style="margin:24px 0">
      <img src="/assets/img/plotera-griesanas-galvina.webp" width="1400" height="667" alt="Griešanas plotera galviņa ar asmeni virs materiāla padeves rullīšiem" loading="lazy">
    </figure>

    <h2>Kas ir plotergriešana</h2>
    <p>Plotergriešana ir darbs, kurā ar griešanas ploteri izgriež uzlīmes, uzrakstus vai termoplēves attēlus. Ploteris izgriež tikai augšējo plēves slāni, un lieko plēvi pēc tam noņem ar rokām.</p>

    <h2>Kam pievērst uzmanību, izvēloties griešanas ploteri</h2>
    <h3>Darba platums</h3>
    <p>Platums nosaka, cik plašu materiālu var ievietot ploterī. Mūsu modeļi ir 71, 86 un 134 cm plati. 134 cm modelim materiāla padeve ir līdz 1350 mm, bet griešanas platums – līdz 1260 mm.</p>
    <h3>Griešanas spiediens</h3>
    <p>Jo plašāks spiediena diapazons, jo vairāk dažādu materiālu var griezt. Plānam papīram vajag mazu spiedienu, biezākai plēvei – lielāku.</p>
    <h3>Precizitāte</h3>
    <p>Mazos burtos un smalkās detaļās precizitāte ir svarīga. Mūsu ploteriem asmens pozicionēšanas precizitāte ir 0,01 mm.</p>
    <h3>Pieslēgumi un operētājsistēma</h3>
    <p>Pārbaudiet, vai ploteris darbosies ar Jūsu datoru. Mūsu ploteriem ir USB un COM pieslēgums, un tie darbojas ar Windows XP, Vista, 7, 8 un 10. Mac netiek atbalstīts.</p>

    <h2>Kur iegādāties griešanas ploteri</h2>
    <p>Modeļi un cenas ir apkopoti lapā <a href="/cenas/">Plotergriezēju cenas</a>. Ja vēlaties padomu par izvēli, <a href="/kontakti/">sazinieties ar mums</a>.</p>
  </div>
</section>
</article>
{CTA_BAND}"""
    article = {
        "@type": "Article",
        "headline": "Kas ir ploteris un kā darbojas griešanas ploteris",
        "inLanguage": "lv",
        "image": f"{SITE}/assets/img/plotera-griesanas-galvina.webp",
        "author": {"@id": f"{SITE}/#org"},
        "publisher": {"@id": f"{SITE}/#org"},
        "datePublished": "2026-10-26",
        "dateModified": TODAY,
        "mainEntityOfPage": f"{SITE}/kas-ir-ploteris/",
    }
    page("/kas-ir-ploteris/", "Kas ir ploteris? Griešanas un drukas plotera atšķirība | Ploteris.lv",
         "Kas ir ploteris, kā darbojas griešanas ploteris un kā tas atšķiras no drukas plotera. Parametri, kam pievērst uzmanību, izvēloties plotergriezēju.",
         body, ld=[article, breadcrumbs_ld(trail, "/kas-ir-ploteris/")], og_type="article", nav_key="/kas-ir-ploteris/")


def build_uses():
    trail = [("Sākums", "/"), ("Pielietojums", None)]
    body = f"""
{breadcrumbs_html(trail)}
<section class="hero">
  <div class="wrap">
    <span class="eyebrow">Pielietojums</span>
    <h1>Ploteris uzlīmēm, termoplēvei un kartonam</h1>
    <p class="lead">Griešanas ploteri izmanto uzlīmju, uzrakstu un tekstila apdrukas izgatavošanai. Zemāk aprakstām materiālus, ko var griezt ar mūsu ploteriem, un modeli, kas der katram darbam.</p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap two-col">
    <div class="prose">
      <h2>Uzlīmju ploteris: vinila plēve</h2>
      <p>Vinila plēve jeb ploterplēve ir galvenais griešanas plotera materiāls. No tās izgriež uzlīmes, uzrakstus un logo.</p>
      <p>Auto uzlīmēm un lieliem baneriem vajag plašu materiālu, tāpēc tiem paredzēts <a href="/ploteris-134-cm/">134 cm ploteris</a>. Nelielām uzlīmēm pietiek ar <a href="/ploteris-71-cm/">71 cm</a> vai <a href="/ploteris-86-cm/">86 cm</a> modeli.</p>
    </div>
    <figure class="hero-img">
      <img src="/assets/img/griesanas-ploteris-stativa.webp" width="1400" height="953" alt="Uzlīmju ploteris uz statīva ar ruļļa turētāju" loading="lazy">
    </figure>
  </div>
</section>

<section class="section">
  <div class="wrap prose">
    <h2>Termoplēve un floks T-krekliem</h2>
    <p>Termoplēve (HTV jeb Flex plēve) un flokētā plēve paredzēta T-kreklu un tekstila apdrukai. Flokētajai plēvei ir samtaina virsma. Ploteris izgriež attēlu, ko pēc tam ar karstumu pārnes uz auduma.</p>
    <p>T-kreklu apdrukai piemērots <a href="/ploteris-86-cm/">86 cm ploteris</a>.</p>

    <h2>Papīrs un kartons</h2>
    <p>Ploteris griež papīru un amatniecības papīru līdz vidējam biezumam, kā arī plānākus kartona veidus. Mājamatniecībai un nelieliem formātiem der <a href="/ploteris-71-cm/">71 cm ploteris</a>.</p>

    <h2>Krāsu maskas lāzergravēšanai</h2>
    <p>Ar ploteri var izgriezt krāsu maskas, ko izmanto kopā ar lāzergravētājiem. Ja Jums jau ir CO2 lāzers vai plānojat to iegādāties, apskatiet <a href="https://bratus.lv/collections/lazeru-lapa">lāzerus vietnē bratus.lv</a>.</p>

    <h2>Materiālu kopsavilkums</h2>
  </div>
  <div class="wrap" style="margin-top:16px">{MATERIALS_TABLE}</div>
</section>
{CTA_BAND}"""
    page("/uzlimju-ploteris/", "Uzlīmju ploteris – vinila un termoplēves griešana | Ploteris.lv",
         "Griešanas ploteris uzlīmēm, auto uzlīmēm, termoplēvei T-krekliem, papīram un kartonam. Kurš plotera modelis der katram darbam.",
         body, ld=[breadcrumbs_ld(trail, "/uzlimju-ploteris/")], nav_key="/uzlimju-ploteris/")


def build_contacts():
    trail = [("Sākums", "/"), ("Kontakti", None)]
    opts = "".join(f'<option value="{m["cm"]} cm">{m["cm"]} cm – {m["price_lv"]} € bez PVN</option>' for m in MODELS)
    body = f"""
{breadcrumbs_html(trail)}
<section class="hero">
  <div class="wrap">
    <span class="eyebrow">Kontakti</span>
    <h1>Plotera pasūtīšana un konsultācija</h1>
    <p class="lead">Zvaniet vai rakstiet, ja vēlaties pasūtīt ploteri vai uzzināt, kurš modelis der Jūsu darbam. Ploteri var pasūtīt arī internetā vietnē bratus.lv.</p>
  </div>
</section>

<section class="section section-alt">
  <div class="wrap two-col">
    <div>
      <h2>Sazinieties ar mums</h2>
      <ul class="contact-list">
        <li><span>Tālrunis</span><a href="tel:{PHONE1_TEL}">{PHONE1}</a></li>
        <li><span>Tālrunis</span><a href="tel:{PHONE2_TEL}">{PHONE2}</a></li>
        <li><span>E-pasts</span><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><span>Pasūtīt internetā</span><a href="{BUY_URL}">bratus.lv</a></li>
        <li><span>Adrese</span>Pliederu iela 22, Ķekava, Ķekavas nov.</li>
        <li><span>Rekvizīti</span>SIA Bratus, reģ. nr. 40203628316</li>
      </ul>
    </div>
    <div>
      <h2>Pieprasījums</h2>
      <form class="form" id="contact-form">
        <div>
          <label for="modelis">Interesējošais modelis</label>
          <select id="modelis" name="modelis">{opts}<option value="nezinu">Vēl nezinu</option></select>
        </div>
        <div>
          <label for="vards">Vārds, uzvārds</label>
          <input id="vards" name="vards" autocomplete="name" required>
        </div>
        <div>
          <label for="talrunis">Tālrunis</label>
          <input id="talrunis" name="talrunis" type="tel" autocomplete="tel" required>
        </div>
        <div>
          <label for="jautajums">Ko plānojat griezt? (neobligāti)</label>
          <textarea id="jautajums" name="jautajums" rows="4"></textarea>
        </div>
        <button class="btn btn-primary" type="submit">Sagatavot e-pastu</button>
        <p class="form-hint">Poga atver Jūsu e-pasta programmu ar aizpildītu vēstuli uz {EMAIL}. Dati netiek sūtīti caur šo vietni.</p>
      </form>
    </div>
  </div>
</section>"""
    page("/kontakti/", "Kontakti – plotera pasūtīšana un konsultācija | Ploteris.lv",
         f"Pasūtiet griešanas ploteri vai saņemiet padomu par modeli: {PHONE1}, {EMAIL}. SIA Bratus, Pliederu iela 22, Ķekava.",
         body, ld=[breadcrumbs_ld(trail, "/kontakti/"), {"@type": "ContactPage", "url": f"{SITE}/kontakti/", "about": {"@id": f"{SITE}/#org"}}],
         nav_key="/kontakti/")


def build_404():
    body = """
<section class="hero">
  <div class="wrap prose">
    <h1>Lapa nav atrasta</h1>
    <p class="lead">Šāda lapa neeksistē vai ir pārvietota. Plotergriezēju modeļus un cenas atradīsiet sākumlapā.</p>
    <div class="btn-row"><a class="btn btn-primary" href="/">Uz sākumlapu</a><a class="btn btn-ghost" href="/cenas/">Cenas</a></div>
  </div>
</section>"""
    page("/404.html", "Lapa nav atrasta | Ploteris.lv", "Šāda lapa ploteris.lv vietnē nav atrasta.", body)
    p = ROOT / "404.html"
    p.write_text(p.read_text(encoding="utf-8").replace('content="index, follow, max-image-preview:large"', 'content="noindex"'), encoding="utf-8")


def build_meta(paths):
    urls = "".join(
        f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in paths
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    build_home()
    for m in MODELS:
        build_model(m)
    build_prices()
    build_uses()
    build_guide()
    build_contacts()
    build_404()
    build_meta(["/", *[f"/{m['slug']}/" for m in MODELS], "/cenas/", "/uzlimju-ploteris/", "/kas-ir-ploteris/", "/kontakti/"])
    print("Gatavs.")
