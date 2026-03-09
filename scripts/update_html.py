import pandas as pd, re, json

# ════════════════════════════════════════════════════════════════
#  FUENTE: solo la hoja "Principal" del Excel de movimientos.
#  La Hoja1 (márgenes) es interna de Tambotorca — nunca se expone.
#  LÓGICA: Subtotal = PRECIO UNIT. COSTO × TOTAL UND VENDIDAS
#           → lo que Tambotorca le debe a Mullerk (al costo).
# ════════════════════════════════════════════════════════════════

COL = {
    'codigo':        0,
    'descripcion':   1,
    'exist_emp':     2,   # Existencia en empaques (stock actual)
    'min_venta':     3,   # Unidades por empaque
    'precio_costo':  4,   # Precio unitario a costo (lo que le debo a Mullerk)
    'precio_venta':  5,   # Precio unitario de venta (PRIVADO — no usar en reporte)
    'precio_emp':    6,   # Precio por empaque (PRIVADO)
    'emp_recibidos': 7,   # Empaques recibidos en consignación
    'emp_vendidos':  8,   # Empaques vendidos
    'und_recibidas': 9,   # Unidades recibidas (consignado)
    'und_vendidas':  10,  # Unidades vendidas
    'facturado':     11,  # Facturado al precio de venta (PRIVADO — no usar)
}

df = pd.read_excel(
    "mnt/Proyecto Mullerk/Movimientos_Consignacion_Mullerk.xlsx",
    sheet_name="Principal", header=0
)
df.columns = list(COL.keys())
df = df.dropna(subset=['codigo'])
df['cod'] = df['codigo'].astype(str).str.strip().str.upper()

# ── Helpers ───────────────────────────────────────────────────────────────
def fmt_units(n):
    n = float(n)
    return f"{int(n):,}" if n == int(n) else f"{n:,.1f}"

def fmt_usd(n):   return f"${float(n):,.2f}"

def bar_color(pct):
    if pct >= 80: return "#f87171"   # rojo  — stock casi agotado
    if pct >= 50: return "#22c55e"   # verde — rotación normal
    return "#60a5fa"                  # azul  — stock abundante

ABONO = 3200.00

CATEGORIES = [
    ("Abrazaderas Acero Inoxidable", "Subtotal Abrazaderas Acero Inoxidable",
     [c for c in df['cod'] if c.startswith('MK-A')]),
    ("Abrazaderas EMT", "Subtotal Abrazaderas EMT",
     [c for c in df['cod'] if c.startswith('MK-EMT')]),
    ("Abrazaderas Galvanizadas", "Subtotal Abrazaderas Galvanizadas",
     [c for c in df['cod'] if c.startswith('MK-G')]),
    ("Cajetines", "Subtotal Cajetines",
     [c for c in df['cod'] if c.startswith('MK-CAJ')]),
    ("Cintas Métricas", "Subtotal Cintas Métricas",
     [c for c in df['cod'] if c.startswith('MK-MET')]),
    ("Mangueras PVC", "Subtotal Mangueras PVC",
     [c for c in df['cod'] if c.startswith('MK-UPVC')]),
    ("Tie Wraps", "Subtotal Tie Wraps",
     [c for c in df['cod'] if c.startswith('MK-TW')]),
]

# ── Construir tbody ───────────────────────────────────────────────────────
cat_subtotals     = {}
prod_subtotals_all = {}
tbody_lines       = []

for cat_label, sub_label, codes in CATEGORIES:
    tbody_lines.append(
        f'        <tr class="cat-row">\n'
        f'            <td colspan="6"><span class="cat-badge">{cat_label}</span></td>\n'
        f'        </tr>'
    )
    cat_total = 0.0
    for cod in codes:
        r = df[df['cod'] == cod].iloc[0]

        und_emp    = float(r['min_venta'])       # unidades por empaque
        consignado = float(r['und_recibidas'])   # total unidades consignadas
        exist_emp  = float(r['exist_emp'])        # stock en empaques
        vendido    = float(r['und_vendidas'])     # unidades vendidas
        costo      = float(r['precio_costo'])     # costo unitario → base del adeudado
        desc       = str(r['descripcion']).strip()

        stock    = exist_emp * und_emp            # stock en unidades
        subtotal = costo * vendido                # lo que se debe a Mullerk
        cat_total += subtotal
        prod_subtotals_all[cod] = (desc, subtotal)

        pct   = (vendido / consignado * 100) if consignado > 0 else 0.0
        color = bar_color(pct)

        tbody_lines.append(
            f'        <tr class="prod-row">\n'
            f'            <td><code>{cod}</code></td>\n'
            f'            <td class="desc">{desc}</td>\n'
            f'            <td class="num">{fmt_units(consignado)}</td>\n'
            f'            <td class="num sold">{fmt_units(vendido)}\n'
            f'                <div class="bar-wrap"><div class="bar-fill" style="width:{pct:.1f}%;background:{color}"></div></div>\n'
            f'                <span class="pct-label">{pct:.1f}%</span>\n'
            f'            </td>\n'
            f'            <td class="num stock">{fmt_units(stock)}</td>\n'
            f'            <td class="num subtotal">{fmt_usd(subtotal)}</td>\n'
            f'        </tr>'
        )

    cat_subtotals[cat_label] = cat_total
    tbody_lines.append(
        f'        <tr class="sub-row">\n'
        f'            <td colspan="5" class="sub-label">{sub_label}</td>\n'
        f'            <td class="num subtotal">{fmt_usd(cat_total)}</td>\n'
        f'        </tr>'
    )

# Totales financieros
total_adeudado = sum(cat_subtotals.values())
stock_total    = sum(
    float(r['exist_emp']) * float(r['min_venta']) * float(r['precio_costo'])
    for _, r in df.iterrows()
)
consig_total   = sum(
    float(r['und_recibidas']) * float(r['precio_costo'])
    for _, r in df.iterrows()
)
saldo       = total_adeudado - ABONO
saldo_class = "credito" if saldo <= 0 else "deuda"
saldo_label = "Crédito a favor de Tambotorca" if saldo <= 0 else "Saldo deudor de Tambotorca"
saldo_val   = f"({fmt_usd(abs(saldo))})" if saldo <= 0 else fmt_usd(saldo)

tbody_lines.append(
    f'          <tr class="total-row">\n'
    f'            <td colspan="5" style="text-align:right;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;color:#9ca3af;">Total Adeudado (USD)</td>\n'
    f'            <td class="num subtotal">{fmt_usd(total_adeudado)}</td>\n'
    f'          </tr>\n'
    f'          <tr class="abono-row">\n'
    f'            <td colspan="5" style="text-align:right;font-size:.82rem;color:#4ade80;">(-) Saldo Abonado</td>\n'
    f'            <td class="num subtotal" style="color:#4ade80;">({fmt_usd(ABONO)})</td>\n'
    f'          </tr>\n'
    f'          <tr class="saldo-row {saldo_class}">\n'
    f'            <td colspan="5" style="text-align:right;font-size:.85rem;font-weight:800;text-transform:uppercase;letter-spacing:.06em;">{saldo_label}</td>\n'
    f'            <td class="num subtotal">{saldo_val}</td>\n'
    f'          </tr>'
)
new_tbody = "\n".join(tbody_lines)

# ── Leer HTML ─────────────────────────────────────────────────────────────
html_path = "mnt/Proyecto Mullerk/Reporte_Consignacion_Mullerk.html"
with open(html_path, encoding='utf-8') as f:
    html = f.read()

# 1. Tbody
html = re.sub(
    r'(<table id="tbl-productos">.*?<tbody>)(.*?)(</tbody>\s*</table>)',
    lambda m: m.group(1) + "\n          \n" + new_tbody + "\n        " + m.group(3),
    html, flags=re.DOTALL
)

# 2. KPIs
html = re.sub(r'(Total Adeudado</div>\s*<div class="value">)[^<]*(</div>)',
              lambda m: m.group(1) + fmt_usd(total_adeudado) + m.group(2), html)
html = re.sub(r'(Stock Actual \(costo\)</div>\s*<div class="value">)[^<]*(</div>)',
              lambda m: m.group(1) + fmt_usd(stock_total) + m.group(2), html)
html = re.sub(r'(Crédito a Favor</div>\s*<div class="value">)[^<]*(</div>)',
              lambda m: m.group(1) + saldo_val + m.group(2), html)


# 4. Gráficos
chart_order = [
    "Abrazaderas Acero Inoxidable", "Cintas Métricas", "Abrazaderas Galvanizadas",
    "Tie Wraps", "Cajetines", "Mangueras PVC", "Abrazaderas EMT"
]
html = re.sub(
    r"(// Grafico 1: Dona por categoria\nnew Chart\([^{]*\{.*?data: \{.*?labels: )(\[.*?\])(.*?datasets: \[\{ data: )(\[.*?\])",
    lambda m: m.group(1) + json.dumps(chart_order, ensure_ascii=False)
            + m.group(3)
            + str([round(cat_subtotals.get(k, 0), 2) for k in chart_order]),
    html, flags=re.DOTALL
)

top10 = sorted(
    [(cod, desc[:24]+("…" if len(desc)>24 else ""), round(sub,2))
     for cod,(desc,sub) in prod_subtotals_all.items()],
    key=lambda x: x[2], reverse=True
)[:10]
html = re.sub(
    r"(// Grafico 2: Top 10 horizontal\nnew Chart\([^{]*\{.*?data: \{.*?labels: )(\[.*?\])(.*?datasets: \[\{.*?data: )(\[.*?\])",
    lambda m: m.group(1) + json.dumps([x[1] for x in top10], ensure_ascii=False)
            + m.group(3)
            + str([x[2] for x in top10]),
    html, flags=re.DOTALL
)
html = re.sub(r"(\{ label: 'Vendido',\s*data: )\[[\d.]+\]",
              lambda m: m.group(1) + f"[{round(total_adeudado,2)}]", html)
html = re.sub(r"(\{ label: 'Stock',\s*data: )\[[\d.]+\]",
              lambda m: m.group(1) + f"[{round(stock_total,2)}]", html)

# 5. Fecha
html = re.sub(r'Reporte generado el \d{2}/\d{2}/\d{4}',
              'Reporte generado el 07/03/2026', html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# ── Resumen ───────────────────────────────────────────────────────────────
print("=== ACTUALIZACIÓN COMPLETADA ===")
print(f"Fuente:               Movimientos_Consignacion_Mullerk.xlsx (hoja Principal)")
print(f"Lógica:               Subtotal = PRECIO UNIT. COSTO × UND VENDIDAS")
print(f"Total consignado:     {fmt_usd(consig_total)}")
print(f"Total Adeudado:       {fmt_usd(total_adeudado)}")
print(f"Stock (costo):        {fmt_usd(stock_total)}")
print(f"Abono recibido:       {fmt_usd(ABONO)}")
print(f"Saldo:                {saldo_val} ({saldo_class})")
print()
print("Subtotales por categoría:")
for k,v in cat_subtotals.items():
    print(f"  {k:<42}: {fmt_usd(v)}")
print()
print("Top 10 productos:")
for i,(cod,desc,sub) in enumerate(top10,1):
    print(f"  {i:2d}. {cod:<20} {desc:<27}: {fmt_usd(sub)}")
