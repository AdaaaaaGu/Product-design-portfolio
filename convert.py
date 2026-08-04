#!/usr/bin/env python3
"""Convert a Claude Design .dc.html component into a standalone HTML page.

Resolves {{ }} template bindings into concrete inline styles / data attributes
and replaces the DCLogic class with plain JavaScript.
"""
import re
import sys
import pathlib

SRC = pathlib.Path(sys.argv[1])
DST = pathlib.Path(sys.argv[2])

html = SRC.read_text(encoding="utf-8")

# ---------------------------------------------------------------- style utils
def css(obj):
    """Turn a dict of JS-style CSS props into a CSS declaration string."""
    out = []
    for k, v in obj.items():
        prop = re.sub(r"(?<!^)([A-Z])", r"-\1", k).lower()
        out.append(f"{prop}:{v}")
    return "; ".join(out)


def btn(active):
    return css({
        "fontFamily": "'Instrument Sans',sans-serif",
        "fontSize": "12px",
        "fontWeight": 500,
        "padding": "5px 12px",
        "border": 0,
        "cursor": "pointer",
        "background": "#FAFAFC" if active else "transparent",
        "color": "#0F1014" if active else "#ACAFB8",
    })


CARD_IMG = css({
    "display": "block",
    "width": "100%",
    "aspectRatio": "16/10",
    "objectFit": "cover",
    "objectPosition": "center",
    "transition": "transform 620ms cubic-bezier(.2,.7,.2,1)",
})

BAR = css({
    "position": "sticky", "top": 0, "zIndex": 50, "display": "flex", "gap": "2px",
    "alignItems": "center", "background": "#0F1014", "padding": "8px 24px",
    "flexWrap": "wrap",
})

# Keyword chip style "C" — the documented default in the handoff README.
KW_ROW = css({"display": "flex", "flexWrap": "wrap", "gap": "6px", "marginTop": "11px"})
KW_ITEM = css({
    "background": "#F3F4F8", "padding": "4px 9px", "fontSize": "10.5px",
    "fontWeight": 600, "letterSpacing": ".06em", "textTransform": "uppercase",
    "color": "#5C5F68", "whiteSpace": "nowrap",
})

SCREENS = ["home", "cognite", "case", "ashley", "pg", "wayhome", "style"]
NAV = {  # binding name -> screen key
    "showHome": "home", "showCognite": "cognite", "showCase": "case",
    "showAshley": "ashley", "showPg": "pg", "showWayhome": "wayhome",
    "showStyle": "style",
}

# ------------------------------------------------------------ strip the shell
html = html.replace('<script src="./support.js"></script>\n', "")
html = re.sub(r'<script type="text/x-dc".*?</script>', "", html, flags=re.S)
html = html.replace("<x-dc>", "").replace("</x-dc>", "")
html = html.replace("<helmet>", "").replace("</helmet>", "")

# Move the (now unwrapped) head content out of <body> and into <head>.
m = re.search(r"<body>\s*(.*?)(<div style=)", html, flags=re.S)
head_content = m.group(1).strip()
html = html[: m.start(1)] + m.group(2) + html[m.end(2):]
html = html.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>Ada Gu — Product Designer</title>\n" + head_content,
)

# ------------------------------------------------------- resolve the bindings
def b(name):
    """Regex matching {{ name }} with flexible whitespace."""
    return r"\{\{\s*" + name + r"\s*\}\}"


# Screen containers: style binding -> data attribute + class, toggled by CSS.
for key in SCREENS:
    binding = "homeDisplay" if key == "home" else f"{key}Display"
    active = ' class="is-on"' if key == "home" else ""
    html = re.sub(
        r'style="' + b(binding) + r'"',
        f'data-screen="{key}"{active}',
        html,
    )

# Preview-bar buttons: click binding -> data-nav, style binding -> real CSS.
for key in SCREENS:
    html = re.sub(r'style="' + b(f"{key}Btn") + r'"',
                  f'style="{btn(key == "home")}"', html)

# Navigation click handlers (bar buttons, card links, next-case bands, logo).
for binding, key in NAV.items():
    html = re.sub(r'onClick="' + b(binding) + r'"', f'data-nav="{key}"', html)

# Card hover is now pure CSS — drop the JS mouse handlers, mark the card.
html = re.sub(r'\s*onMouseEnter="' + b(r"enter\w+") + r'"', " data-card", html)
html = re.sub(r'\s*onMouseLeave="' + b("leaveCard") + r'"', "", html)

# Card images, keyword chips, preview bar.
html = re.sub(r'style="' + b(r"img(Cog|Hal|Ash|Pg|Way)") + r'"',
              f'style="{CARD_IMG}"', html)
html = re.sub(r'style="' + b("kwRow") + r'"', f'style="{KW_ROW}"', html)
html = re.sub(r'style="' + b("kwItem") + r'"', f'style="{KW_ITEM}"', html)
html = re.sub(r'style="' + b("barStyle") + r'"', f'style="{BAR}"', html)
html = re.sub(r'\s*onSubmit="' + b("onSubmit") + r'"', " data-nosubmit", html)

# ------------------------------------------------------------ injected assets
EXTRA_CSS = """
  <style>
    /* Screen routing — only the active screen is shown. */
    [data-screen]{display:none}
    [data-screen].is-on{display:block}
    /* Project card image lift (was a JS hover state in the design component). */
    [data-card] img{transform:scale(1)}
    [data-card]:hover img{transform:scale(1.035)}
    @media (prefers-reduced-motion:reduce){
      [data-card] img,[data-card]:hover img{transform:none; transition:none}
    }
    /* Stand-in for artwork not yet supplied. Drop the real file in and it
       replaces itself — no markup change needed. */
    .img-missing{
      display:flex; align-items:center; justify-content:center; text-align:center;
      background:#F3F4F8; border:1px dashed #C3C3BE; color:#8A8D96;
      padding:16px; font-size:11px; line-height:1.5; letter-spacing:.04em;
      overflow:hidden;
    }
    /* Too small to caption (logo marks and the like) — just show the box. */
    .img-missing[data-tiny]{padding:0}
    .img-missing span{max-width:26em}
    .img-missing code{
      display:block; margin-top:6px; font-size:10px; color:#ACAFB8;
      letter-spacing:0; word-break:break-all;
    }
  </style>
"""

RUNTIME = """
<script>
(function () {
  'use strict';

  var screens = document.querySelectorAll('[data-screen]');
  var navButtons = document.querySelectorAll('[data-nav]');

  function paintNav(active) {
    document.querySelectorAll('.preview-bar [data-nav]').forEach(function (el) {
      var on = el.getAttribute('data-nav') === active;
      el.style.background = on ? '#FAFAFC' : 'transparent';
      el.style.color = on ? '#0F1014' : '#ACAFB8';
    });
  }

  function show(name) {
    screens.forEach(function (el) {
      el.classList.toggle('is-on', el.getAttribute('data-screen') === name);
    });
    paintNav(name);
    window.scrollTo(0, 0);
    spy();
  }

  navButtons.forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      show(el.getAttribute('data-nav'));
    });
  });

  // Case-study scroll spy: highlight the table-of-contents entry in view.
  function spy() {
    var links = [].slice.call(document.querySelectorAll('[data-toc]'))
      .filter(function (a) { return a.offsetParent !== null; });
    if (!links.length) return;
    var idx = 0;
    links.forEach(function (a, i) {
      var h = document.getElementById(a.getAttribute('data-toc'));
      if (h && h.getBoundingClientRect().top < 160) idx = i;
    });
    links.forEach(function (a, i) {
      a.style.color = i === idx ? '#0F1014' : '#8A8D96';
      a.style.borderLeftColor = i === idx ? (a.dataset.acc || '#DD0F26') : '#E6E8EE';
    });
  }

  document.addEventListener('scroll', spy, { passive: true });

  document.querySelectorAll('[data-nosubmit]').forEach(function (f) {
    f.addEventListener('submit', function (e) { e.preventDefault(); });
  });

  // Artwork that hasn't been supplied yet renders as a labelled placeholder
  // that keeps the intended aspect ratio, so layout still reads correctly.
  function placeholder(img) {
    if (img.dataset.placeheld) return;
    img.dataset.placeheld = '1';
    var box = document.createElement('div');
    box.className = 'img-missing';
    box.style.cssText = img.getAttribute('style') || '';
    box.style.aspectRatio = getComputedStyle(img).aspectRatio !== 'auto'
      ? getComputedStyle(img).aspectRatio : '16/10';
    box.style.transform = '';
    var rect = img.getBoundingClientRect();
    if (rect.width && rect.width < 140) {
      box.setAttribute('data-tiny', '');
      box.title = img.getAttribute('src');
    } else {
      var label = img.getAttribute('alt') || 'Image';
      box.innerHTML = '<span>' + label +
        '<code>' + img.getAttribute('src') + '</code></span>';
    }
    img.replaceWith(box);
  }

  document.querySelectorAll('img').forEach(function (img) {
    if (img.complete && !img.naturalWidth) placeholder(img);
    else img.addEventListener('error', function () { placeholder(img); });
  });

  spy();
})();
</script>
"""

html = html.replace("</head>", EXTRA_CSS + "</head>")
html = html.replace("</body>", RUNTIME + "</body>")

# Tag the preview bar so its buttons can be restyled independently of card links.
html = html.replace(f'<div style="{BAR}">', f'<div class="preview-bar" style="{BAR}">')

DST.write_text(html, encoding="utf-8")

leftover = re.findall(r"\{\{[^}]*\}\}", html)
print("wrote:", DST)
print("unresolved bindings:", len(leftover), sorted(set(leftover)) if leftover else "none")
