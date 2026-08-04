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

# `display` is deliberately omitted — the .preview-bar CSS rules own it, and an
# inline display would outrank them.
BAR = css({
    "position": "sticky", "top": 0, "zIndex": 50, "gap": "2px",
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

# ------------------------------------------------------- homepage nav anchors
# "Work" and "Lab" shipped as href="#" placeholders. Point them at the project
# grid and the lab section, following the scroll-margin-top pattern the
# existing #contact anchor already uses.
html, n_work = re.subn(
    r'<main data-r="cards" style="',
    '<main id="work" data-r="cards" style="scroll-margin-top:24px; ',
    html,
)
html, n_lab = re.subn(
    r'<section>(\s*<div style="[^"]*">Lab</div>)',
    r'<section id="lab" style="scroll-margin-top:24px;">\1',
    html,
)
html, n_wlink = re.subn(
    r'<a href="#">Work</a>', '<a href="#work" data-jump="work">Work</a>', html)
html, n_llink = re.subn(
    r'<a href="#">Lab</a>', '<a href="#lab" data-jump="lab">Lab</a>', html)

assert n_work == 1, f"expected 1 project grid, patched {n_work}"
assert n_lab == 1, f"expected 1 lab section, patched {n_lab}"
print(f"anchors: #work x{n_work}, #lab x{n_lab}; "
      f"links rewired: Work x{n_wlink}, Lab x{n_llink}")

# ------------------------------------------------------------ injected assets
EXTRA_CSS = """
  <style>
    /* Screen routing — only the active screen is shown. */
    [data-screen]{display:none}
    [data-screen].is-on{display:block}
    /* Design-time screen switcher. Hidden from visitors; append ?preview to
       the URL to bring it back while working on the pages. */
    .preview-bar{display:none}
    .preview-bar.is-shown{display:flex}
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

  // The screen switcher is a design-time tool, not part of the site.
  // Both forms are accepted: ?preview works when the page is served over
  // http, #preview survives when it is opened straight off disk.
  var bar = document.querySelector('.preview-bar');
  if (bar && /preview/.test(location.search + location.hash)) {
    bar.classList.add('is-shown');
  }

  function paintNav(active) {
    document.querySelectorAll('.preview-bar [data-nav]').forEach(function (el) {
      var on = el.getAttribute('data-nav') === active;
      el.style.background = on ? '#FAFAFC' : 'transparent';
      el.style.color = on ? '#0F1014' : '#ACAFB8';
    });
  }

  function show(name, keepScroll) {
    screens.forEach(function (el) {
      el.classList.toggle('is-on', el.getAttribute('data-screen') === name);
    });
    paintNav(name);
    if (!keepScroll) window.scrollTo(0, 0);
    spy();
  }

  navButtons.forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      show(el.getAttribute('data-nav'));
    });
  });

  // "Work" and "Lab" live in the nav on every screen, so from a case study
  // they have to return to the homepage before scrolling to the section.
  document.querySelectorAll('[data-jump]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      e.preventDefault();
      var target = document.getElementById(el.getAttribute('data-jump'));
      if (!target) return;
      var home = document.querySelector('[data-screen="home"]');
      var alreadyHome = home && home.classList.contains('is-on');
      show('home', true);
      // Gliding across a screen change would scroll through the whole page.
      var jump = function () {
        target.scrollIntoView({
          behavior: alreadyHome ? 'smooth' : 'instant',
          block: 'start'
        });
      };
      // A screen that was display:none has no layout yet, so its offsets are
      // stale until the browser reflows. Wait a frame before measuring.
      if (alreadyHome) jump();
      else requestAnimationFrame(jump);
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

# ------------------------------------------------- embedded motion component
# The Halliburton case study carries a <dc-import name="Pipeline Motion"> slot.
# That tag only resolves inside Claude Design, so the markup and logic from
# Pipeline Motion.dc.html get inlined here instead.

MOTION_CSS = """
  <style>
    @keyframes pp-flow{to{stroke-dashoffset:-64}}
    @media (prefers-reduced-motion:reduce){
      #pp-root [style*="pp-flow"]{animation:none !important}
    }
  </style>
"""

MOTION_JS = """
<script>
(function () {
  'use strict';
  var root = document.getElementById('pp-root');
  if (!root) return;

  var SPEED = 1000, DWELL = 1900, LOOP = true;
  var AUTOPLAY = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var SEG = [[-520,-180],[-180,330],[330,780],[780,1050],
             [1050,1240],[1240,1560],[1560,1780],[1780,2120]];
  var TU = [440,440,440,440,440,440,440,440];
  var BU = [560,560,560,560,560,560,560,560];
  var TS = [432,448,402,430,466,396,456,438];
  var BS = [566,556,574,604,548,566,594,552];
  var JN = [{x:140,i:1,w:72,side:'top'},{x:1400,i:5,w:72,side:'bot'}];
  var VB = [[540,370,520,260],[240,210,1160,580],
            [-400,-100,2400,1200],[-400,-100,2400,1200]];

  var q = function (s) { return root.querySelector(s); };
  var svg = q('#pp-svg'), fill = q('#pp-fill');
  var tops = [q('#pp-top0'), q('#pp-top1')];
  var bots = [q('#pp-bot0'), q('#pp-bot1')];
  var secs = [q('#pp-sec1'), q('#pp-sec2')];
  var labels = q('#pp-labels'), marks = q('#pp-marks');
  var caps = [q('#pp-cap0'), q('#pp-cap1'), q('#pp-cap2'), q('#pp-cap3')];
  var btns = [q('#pp-btn0'), q('#pp-btn1'), q('#pp-btn2'), q('#pp-btn3')];

  var p = 0, active = 0, raf = null, timers = [], started = false;

  function clearTimers() { timers.forEach(clearTimeout); timers = []; }
  function ease(t) {
    return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2;
  }

  function seq(vals) {
    var pts = [];
    SEG.forEach(function (s, i) {
      pts.push([s[0], vals[i]]);
      pts.push([s[1], vals[i]]);
    });
    return pts;
  }

  // Opens a gap in the run where a junction branches off.
  function split(pts, vals, side, openFrac) {
    var cuts = JN.map(function (j, idx) {
      return { x:j.x, side:j.side, w:j.w * (openFrac[idx] || 0), y:vals[j.i] };
    }).filter(function (c) { return c.side === side && c.w > 0.5; });

    var lines = [], cur = [pts[0]];
    for (var k = 1; k < pts.length; k++) {
      var a = pts[k-1], b = pts[k];
      var cut = cuts.find(function (c) {
        return a[1] === b[1] &&
               c.x > Math.min(a[0], b[0]) && c.x < Math.max(a[0], b[0]);
      });
      if (cut) {
        cur.push([cut.x - cut.w, cut.y]);
        lines.push(cur);
        cur = [[cut.x + cut.w, cut.y]];
      }
      cur.push(b);
    }
    lines.push(cur);
    return lines.map(function (l) {
      return l.map(function (pt) {
        return pt[0].toFixed(1) + ',' + pt[1].toFixed(1);
      }).join(' ');
    });
  }

  function apply(pos) {
    var i0 = Math.min(Math.max(0, Math.floor(pos)), VB.length - 2);
    var a = VB[i0], b = VB[i0 + 1], f = pos - i0;
    svg.setAttribute('viewBox', a.map(function (v, i) {
      return (v + (b[i] - v) * f).toFixed(1);
    }).join(' '));

    var m = Math.min(1, Math.max(0, pos));
    var T = TU.map(function (u, i) { return u + (TS[i] - u) * m; });
    var B = BU.map(function (u, i) { return u + (BS[i] - u) * m; });
    var top = seq(T), bot = seq(B);

    fill.setAttribute('points',
      top.concat(bot.slice().reverse()).map(function (pt) {
        return pt[0].toFixed(1) + ',' + pt[1].toFixed(1);
      }).join(' '));

    var op = function (lo, hi) {
      return Math.min(1, Math.max(0, (pos - lo) / (hi - lo)));
    };
    var o = [op(1.0, 1.5), op(1.2, 1.75)];
    var set = function (els, lines) {
      els.forEach(function (el, i) {
        if (el) el.setAttribute('points', lines[i] || '');
      });
    };
    set(tops, split(top, T, 'top', o));
    set(bots, split(bot, B, 'bot', o));

    secs.forEach(function (el, i) { if (el) el.style.opacity = o[i]; });
    if (labels) labels.style.opacity = op(1.5, 2) - 0.42 * op(2.2, 2.85);
    if (marks) marks.style.opacity = op(2.15, 2.9);

    var step = pos < 0.55 ? 0 : (pos < 1.55 ? 1 : (pos < 2.55 ? 2 : 3));
    if (step !== active) {
      active = step;
      caps.forEach(function (el, i) {
        if (el) el.style.opacity = i === step ? 1 : 0;
      });
      btns.forEach(function (el, i) {
        if (!el) return;
        el.style.borderTopColor = i === step ? '#DD0F26' : 'transparent';
        el.style.color = i === step ? '#0F1014' : '#8A8D96';
      });
    }
  }

  function animateTo(n) {
    cancelAnimationFrame(raf);
    var from = p, to = n;
    if (Math.abs(to - from) < 0.001) { apply(to); return; }
    var d = Math.max(420, SPEED * Math.abs(to - from));
    var t0 = performance.now();
    (function tick(now) {
      var t = Math.min(1, ((now || performance.now()) - t0) / d);
      p = from + (to - from) * ease(t);
      apply(p);
      if (t < 1) raf = requestAnimationFrame(tick);
    })(t0);
  }

  function autoplay(lead) {
    var leg = SPEED + DWELL;
    var a = lead == null ? 600 : lead;
    timers.push(setTimeout(function () { animateTo(1); }, a));
    timers.push(setTimeout(function () { animateTo(2); }, a + leg));
    timers.push(setTimeout(function () { animateTo(3); }, a + leg * 2 + 400));
    if (!LOOP) return;
    timers.push(setTimeout(function () {
      p = 0; active = -1; apply(0); autoplay(DWELL);
    }, a + leg * 2 + 400 + SPEED + DWELL + 1400));
  }

  btns.forEach(function (b, i) {
    if (b) b.addEventListener('click', function () { clearTimers(); animateTo(i); });
  });

  var replay = q('#pp-replay');
  if (replay) replay.addEventListener('click', function () {
    clearTimers();
    cancelAnimationFrame(raf);
    p = 0; active = -1; apply(0);
    autoplay();
  });

  apply(0);

  // Hold until the diagram is actually on screen before playing.
  if (AUTOPLAY && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && !started) { started = true; autoplay(); }
      });
    }, { threshold: 0.45 });
    io.observe(root);
  }
})();
</script>
"""


def motion_markup():
    """Pull the Pipeline Motion markup out of its own .dc.html component."""
    src = SRC.with_name("Pipeline Motion.dc.html")
    text = src.read_text(encoding="utf-8")
    body = re.search(r"</helmet>(.*?)</x-dc>", text, flags=re.S).group(1)
    return body.replace('ref="{{ rootRef }}"', 'id="pp-root"').strip()


html = re.sub(
    r'<dc-import name="Pipeline Motion"[^>]*></dc-import>',
    lambda _: motion_markup(),
    html,
)

html = html.replace("</head>", EXTRA_CSS + MOTION_CSS + "</head>")
html = html.replace("</body>", RUNTIME + MOTION_JS + "</body>")

# Tag the preview bar so its buttons can be restyled independently of card links.
html = html.replace(f'<div style="{BAR}">', f'<div class="preview-bar" style="{BAR}">')

DST.write_text(html, encoding="utf-8")

leftover = re.findall(r"\{\{[^}]*\}\}", html)
print("wrote:", DST)
print("unresolved bindings:", len(leftover), sorted(set(leftover)) if leftover else "none")
