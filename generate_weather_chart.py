import pandas as pd, json, os

# ── CONFIG ───────────────────────────────────────────────────────────────────
# Add or remove CSV files here. City name is taken from the filename.
# Exception: if the filename is "export", rename it below in load_city().
CSV_FILES = [
    'Data/Amsterdam.csv',
    'Data/Braunschweig.csv',
    'Data/Giethoorn.csv',
]

CURRENT_YEAR = 2026   # highlighted year

# year: (hex color, opacity 0-1, line width px)
YEAR_STYLES = {
    2023: ('#888888', 0.45, 1.4),
    2024: ('#FF9800', 0.45, 1.4),
    2025: ('#4CAF50', 0.45, 1.4),
    2026: ('#E91E63', 1.0,  2.5),
}
DEFAULT_STYLE = ('#aaaaaa', 0.45, 1.4)   # fallback for unknown years

OUTPUT = 'weather_comparison.html'
# ─────────────────────────────────────────────────────────────────────────────


def load_city(path):
    city = os.path.splitext(os.path.basename(path))[0]
    if city.lower() == 'export':
        city = 'Bad Pyrmont'
    df = pd.read_csv(path)
    df['date']  = pd.to_datetime(df['date'])
    df['year']  = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day']   = df['date'].dt.day
    df['plot_date'] = pd.to_datetime(
        dict(year=2000, month=df['month'], day=df['day']), errors='coerce'
    )
    df = df.dropna(subset=['plot_date'])
    df['x'] = df['plot_date'].dt.strftime('%Y-%m-%d')
    return city, df


def make_city_data(df):
    out = {}
    for key in ['tavg', 'tmax', 'tmin']:
        out[key] = {}
        for year in sorted(df['year'].unique()):
            sub = df[df['year'] == year].sort_values('plot_date')
            out[key][str(year)] = [
                {'x': r['x'], 'y': None if pd.isna(r[key]) else round(float(r[key]), 1)}
                for _, r in sub.iterrows()
            ]
    # Add rainfall data grouped by year (only values >= 2mm)
    out['prcp'] = {}
    for year in sorted(df['year'].unique()):
        sub = df[df['year'] == year].sort_values('plot_date')
        out['prcp'][str(year)] = [
            {'x': r['x'], 'y': round(float(r['prcp']), 1) if pd.notna(r['prcp']) and float(r['prcp']) >= 2 else None}
            for _, r in sub.iterrows()
        ]
    return out


def build_payload():
    cities, all_years = {}, set()
    for path in CSV_FILES:
        city, df = load_city(path)
        cities[city] = make_city_data(df)
        all_years |= set(df['year'].unique().tolist())

    all_years = sorted(all_years)
    style = lambda y, i: YEAR_STYLES.get(y, DEFAULT_STYLE)[i]
    return {
        'cities':       cities,
        'years':        [str(y) for y in all_years],
        'current_year': str(CURRENT_YEAR),
        'year_colors':  {str(y): style(y, 0) for y in all_years},
        'year_opacities': {str(y): style(y, 1) for y in all_years},
        'year_widths':  {str(y): style(y, 2) for y in all_years},
    }


def render_html(payload):
    data_js = f"const DATA = {json.dumps(payload)};"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weather Temperature Comparison</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.1.0/dist/chartjs-plugin-zoom.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #1a1a2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; padding: 24px; }}
  h1 {{ text-align: center; font-size: 18px; margin-bottom: 6px; color: #e0e0e0; font-weight: 600; }}
  .subtitle {{ text-align:center; font-size:12px; color:#778; margin-bottom:18px; }}
  #tabs {{ display:flex; justify-content:center; gap:8px; margin-bottom:18px; flex-wrap:wrap; }}
  .tab {{
    padding: 7px 20px; border-radius: 20px; cursor: pointer; font-size:13px;
    border: 1px solid #334466; background: #0f3460; color: #b0b0b0; transition: all .2s;
  }}
  .tab.active {{ background:#1565c0; border-color:#2196F3; color:#fff; font-weight:600; }}
  #legend {{ display:flex; justify-content:center; gap:10px; margin-bottom:18px; flex-wrap:wrap; }}
  .leg-item {{
    display:flex; align-items:center; gap:7px; background:#0f3460; border:1px solid #334466;
    border-radius:6px; padding:6px 14px; cursor:pointer; user-select:none; transition: opacity .2s;
  }}
  .leg-item.hidden {{ opacity:.3; }}
  .leg-item.current-year {{ border-color: #E91E63; box-shadow: 0 0 6px #E91E6355; }}
  .leg-swatch {{ width:28px; height:3px; border-radius:2px; }}
  .leg-label {{ font-size:13px; color:#e0e0e0; }}
  .chart-wrap {{ background:#16213e; border-radius:10px; padding:16px 16px 8px; margin-bottom:18px; }}
  .chart-title {{ font-size:13px; font-weight:600; color:#e0e0e0; margin-bottom:10px; }}
  canvas {{ width:100% !important; height:220px !important; }}
  #reset-btn {{ padding:7px 20px; border-radius:20px; cursor:pointer; font-size:13px; border:1px solid #334466; background:#0f3460; color:#b0b0b0; transition:all .2s; margin-left:10px; }}
  #reset-btn:hover {{ background:#1565c0; border-color:#2196F3; color:#fff; }}
  #controls {{ display:flex; justify-content:center; align-items:center; margin-bottom:18px; }}
</style>
</head>
<body>
<h1 id="page-title">Weather Temperature Comparison</h1>
<p class="subtitle">Click a year to toggle it on/off across all charts</p>
<div id="tabs"></div>
<div id="legend"></div>
<div id="controls"><button id="reset-btn">Reset View</button></div>
<div class="chart-wrap"><div class="chart-title">Average Temperature</div><canvas id="c0"></canvas></div>
<div class="chart-wrap"><div class="chart-title">Highest Temperature</div><canvas id="c1"></canvas></div>
<div class="chart-wrap"><div class="chart-title">Lowest Temperature</div><canvas id="c2"></canvas></div>
<script>
{data_js}
const KEYS='tavg tmax tmin'.split(' ');
const YEARS=DATA.years, CURRENT=DATA.current_year;
const COLORS=DATA.year_colors, OPACITIES=DATA.year_opacities, WIDTHS=DATA.year_widths;
const CITIES=Object.keys(DATA.cities);
let activeCity=CITIES[0];
const hidden={{}};
function hexToRgba(hex,a){{const r=parseInt(hex.slice(1,3),16),g=parseInt(hex.slice(3,5),16),b=parseInt(hex.slice(5,7),16);return `rgba(${{r}},${{g}},${{b}},${{a}})`;}}
function makeDatasets(city,key){{
  if(key==='prcp'){{
    return YEARS.map(yr=>({{label:yr+'_prcp',data:(DATA.cities[city][key][yr]||[]),backgroundColor:hexToRgba(COLORS[yr],0.6),borderWidth:0,barThickness:'flex',yAxisID:'y1',parsing:{{xAxisKey:'x',yAxisKey:'y'}},hidden:!!hidden[yr],order:1}}));
  }}
  return YEARS.map(yr=>({{label:yr,data:(DATA.cities[city][key][yr]||[]),borderColor:hexToRgba(COLORS[yr],OPACITIES[yr]),backgroundColor:'transparent',borderWidth:WIDTHS[yr],pointRadius:0,tension:0.25,parsing:{{xAxisKey:'x',yAxisKey:'y'}},hidden:!!hidden[yr],order:yr===CURRENT?0:2}}));
}}const scales={{x:{{type:'time',time:{{unit:'month',displayFormats:{{month:'MMM'}}}},min:'2000-01-01',max:'2000-12-31',ticks:{{color:'#b0b0b0',font:{{size:10}}}},grid:{{color:'#334466',lineWidth:0.5}}}},y:{{position:'left',ticks:{{color:'#b0b0b0',font:{{size:10}},callback:v=>v+' °C'}},grid:{{color:'#334466',lineWidth:0.5}},border:{{color:'#334'}}}},y1:{{position:'right',ticks:{{color:'#6ba3d4',font:{{size:10}},callback:v=>v+' mm'}},grid:{{drawOnChartArea:false}},border:{{color:'#334'}},title:{{display:true,text:'Rainfall',color:'#6ba3d4'}}}}}};
const basePlugins={{legend:{{display:false}},tooltip:{{backgroundColor:'#0f3460',borderColor:'#334466',borderWidth:1,titleColor:'#e0e0e0',bodyColor:'#b0b0b0',callbacks:{{title:items=>{{const d=new Date(items[0].parsed.x);return d.toLocaleDateString('en',{{month:'short',day:'numeric'}})}},label:ctx=>`${{ctx.dataset.label}}: ${{ctx.parsed.y!=null?ctx.parsed.y.toFixed(1)+(ctx.dataset.yAxisID==='y1'?' mm':' °C'):'–'}}`}}}},zoom:{{zoom:{{wheel:{{enabled:true,speed:0.1,min:'original'}},pinch:{{enabled:true}},mode:'xy'}},pan:{{enabled:true,mode:'xy'}}}}}};
const charts=KEYS.map((key,idx)=>{{const ctx=document.getElementById('c'+idx).getContext('2d');const datasets=[...makeDatasets(activeCity,key)];if(key==='tavg')datasets.unshift(...makeDatasets(activeCity,'prcp'));return new Chart(ctx,{{type:'line',data:{{datasets:datasets}},options:{{animation:false,responsive:true,maintainAspectRatio:false,interaction:{{mode:'index',intersect:false}},plugins:basePlugins,scales}}}})}}); 
function resetZoom(){{charts.forEach(ch=>{{ch.resetZoom();}});}};
document.getElementById('reset-btn').addEventListener('click',resetZoom);
function switchCity(city){{activeCity=city;document.getElementById('page-title').textContent=`Weather Temperature Comparison — ${{city}}`;document.querySelectorAll('.tab').forEach(t=>t.classList.toggle('active',t.dataset.city===city));charts.forEach((ch,idx)=>{{const key=KEYS[idx];let datasets=makeDatasets(city,key);if(key==='tavg')datasets=[...makeDatasets(city,'prcp'),...datasets];ch.data.datasets=datasets;ch.data.datasets.forEach(ds=>{{ds.hidden=!!hidden[ds.label]}});ch.update()}});}}
const tabsEl=document.getElementById('tabs');
CITIES.forEach(city=>{{const t=document.createElement('div');t.className='tab'+(city===activeCity?' active':'');t.dataset.city=city;t.textContent=city;t.addEventListener('click',()=>switchCity(city));tabsEl.appendChild(t);}});
const legEl=document.getElementById('legend');
YEARS.forEach(yr=>{{const item=document.createElement('div');item.className='leg-item'+(yr===CURRENT?' current-year':'');item.dataset.year=yr;item.innerHTML=`<div class="leg-swatch" style="background:${{COLORS[yr]}}"></div><span class="leg-label">${{yr}}${{yr===CURRENT?' ★':''}}</span>`;item.addEventListener('click',()=>{{hidden[yr]=!hidden[yr];item.classList.toggle('hidden',hidden[yr]);charts.forEach(ch=>{{ch.data.datasets.forEach(ds=>{{if(ds.label===yr||ds.label===yr+'_prcp'){{ds.hidden=hidden[yr];}}}});ch.update()}});}}); legEl.appendChild(item);}});

switchCity(activeCity);
</script>
</body>
</html>"""


if __name__ == '__main__':
    payload = build_payload()
    html = render_html(payload)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Saved → {OUTPUT}")
    print(f"Cities: {list(payload['cities'].keys())}")
    print(f"Years:  {payload['years']}")
