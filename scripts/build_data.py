"""
Aggregate all data sources into dashboard_data.json.
Reads: Square historical CSVs + Toast daily exports.
Writes: data/dashboard_data.json
"""
import csv, json, os, re
from collections import defaultdict

def parse_dollar(v):
    """Strip $ and parse as float, handling empty/None."""
    if not v: return 0.0
    return float(re.sub(r'[,$]', '', str(v).strip()) or '0')

# --- Category classification for Square items ---
FOOD_KEYWORDS = [
    'cheese', 'charcuterie', 'flatbread', 'burger', 'salad', 'sandwich',
    'burrata', 'oyster', 'crabcake', 'ceviche', 'risotto', 'fish',
    'lamb', 'steak', 'medallion', 'cookie', 'dessert', 'chocolate',
    'cake', 'bread', 'soup', 'chips', 'fries', 'onion ring', 'slider',
    'taco', 'nacho', 'hummus', 'olive', 'bruschetta', 'prosciutto',
    'pizza', 'pasta', 'ravioli', 'gnocchi', 'risotto', 'caprese',
    'antipast', 'arancin', 'crostini', 'food', 'lunch', 'dinner',
    'brunch', 'appetizer', 'entree', 'plate', 'board', 'mezze',
    'mac & cheese', 'mac and cheese', 'pulled pork', 'wing',
    'caviar', 'truffle', 'foie gras', 'pate', 'terrine'
]
LIQUOR_KEYWORDS = [
    'vodka', 'gin', 'tequila', 'rum', 'whiskey', 'whisky', 'bourbon',
    'scotch', 'cognac', 'brandy', 'mezcal', 'margarita', 'martini',
    'cocktail', 'mojito', 'negroni', 'old fashioned', 'manhattan',
    'spritz', 'aperol', 'shot', 'espresso martini', 'paloma',
    'cosmopolitan', 'daiquiri', 'sidecar', 'gimlet', 'highball',
    'tito', 'belvedere', 'grey goose', 'hendrick', 'tanqueray',
    'bombay', 'bulleit', 'maker', 'woodford', 'knob creek',
    'don julio', 'patron', 'casamigos', 'hennessy', 'remy',
    'jack daniel', 'jameson', 'fireball', 'redbull', 'red bull',
    'don fulano', 'glenmarengue'
]
BEER_KEYWORDS = [
    'beer', 'ipa', 'lager', 'ale', 'stout', 'pilsner', 'porter',
    'hefeweizen', 'wheat', 'cider', 'seltzer', 'corona', 'modelo',
    'heineken', 'stella', 'bud', 'coors', 'miller', 'lagunitas',
    'sierra nevada', 'firestone', 'anderson valley'
]
NA_KEYWORDS = [
    'water', 'soda', 'coke', 'sprite', 'ginger', 'tonic', 'juice',
    'lemonade', 'coffee', 'espresso', 'tea', 'sparkling', 'pellegrino',
    'perrier', 'san pellegrino', 'na ', 'non-alc', 'non alc',
    'mocktail', 'zero proof'
]
MARKET_KEYWORDS = ['market']
RETAIL_KEYWORDS = ['retail', 'merchandise', 'gift card', 'e-gift']

def classify_item(name):
    """Classify a Square item by name into a category."""
    low = name.lower().strip()
    if low.startswith('night ') or low.startswith('night-'):
        return 'Night Wines'
    if any(k in low for k in MARKET_KEYWORDS) and any(k in low for k in FOOD_KEYWORDS):
        return 'Food'
    if any(k in low for k in MARKET_KEYWORDS):
        return 'Market'
    if any(k in low for k in FOOD_KEYWORDS):
        return 'Food'
    if any(k in low for k in LIQUOR_KEYWORDS):
        return 'Liquor'
    if any(k in low for k in BEER_KEYWORDS):
        return 'Beer'
    if any(k in low for k in NA_KEYWORDS):
        return 'NA Beverage'
    if any(k in low for k in RETAIL_KEYWORDS):
        return 'Retail'
    # Most remaining items at The Saint are wine
    if any(w in low for w in ['bottle', 'btl', 'btg', 'glass', 'half glass', 'flight', 'tasting']):
        return 'Wine'
    if any(w in low for w in ['cabernet', 'merlot', 'pinot', 'chardonnay', 'sauvignon',
                               'syrah', 'zinfandel', 'malbec', 'tempranillo', 'sangiovese',
                               'nebbiolo', 'grenache', 'mourvedre', 'viognier', 'riesling',
                               'gewurz', 'champagne', 'prosecco', 'rose', 'rosé',
                               'bordeaux', 'burgundy', 'barolo', 'chianti', 'rioja',
                               'chablis', 'sancerre', 'chateau', 'château', 'domaine',
                               'estate', 'vineyard', 'winery', 'reserve', 'vintage']):
        return 'Wine'
    return 'Other'

DATA = 'data'
SQ = DATA + '/square_historical'
EXPORTS = DATA + '/exports'
OUT = DATA + '/dashboard_data.json'

data = {}

# --- Monthly data ---
monthly = []

# Square monthly
sq_monthly = SQ + '/monthly_summary.csv'
if os.path.exists(sq_monthly):
    with open(sq_monthly) as f:
        for r in csv.DictReader(f):
            monthly.append({
                'm': r['Month'], 's': 'SQ',
                'ns': round(float(r['Net Sales']), 2),
                't': round(float(r['Tips']), 2),
                'o': int(r['Orders']),
                'i': int(r['Items Sold'])
            })

# Toast monthly (from historical folder if present)
toast_hist = DATA + '/historical'
if os.path.isdir(toast_hist):
    for m in sorted(os.listdir(toast_hist)):
        p = os.path.join(toast_hist, m)
        if not os.path.isdir(p):
            continue
        try:
            ns = float(list(csv.DictReader(open(p + '/Net sales summary.csv')))[0]['Net sales'])
            tips = float(list(csv.DictReader(open(p + '/Tip summary.csv')))[0]['Total tips'])
            rows = list(csv.DictReader(open(p + '/Service Daypart summary.csv')))
            t = [x for x in rows if x['Service / day part'] == 'Total']
            orders = int(t[0]['Orders']) if t else 0
            cats = list(csv.DictReader(open(p + '/Sales category summary.csv')))
            ct = [x for x in cats if x['Sales category'] == 'Total']
            items = int(float(ct[0]['Items'])) if ct else 0
            monthly.append({'m': m, 's': 'T', 'ns': round(ns, 2), 't': round(tips, 2), 'o': orders, 'i': items})
        except Exception as e:
            print(f"  Warning: Could not process {m}: {e}")

# Toast monthly from daily exports (aggregate)
if os.path.isdir(EXPORTS):
    toast_monthly = defaultdict(lambda: {'ns': 0, 't': 0, 'o': 0, 'i': 0})
    for dd in sorted(os.listdir(EXPORTS)):
        if not dd.isdigit() or len(dd) != 8:
            continue
        m_key = dd[:4] + '-' + dd[4:6]
        order_file = os.path.join(EXPORTS, dd, 'OrderDetails.csv')
        item_file = os.path.join(EXPORTS, dd, 'ItemSelectionDetails.csv')

        if os.path.exists(order_file):
            try:
                with open(order_file) as f:
                    for r in csv.DictReader(f):
                        if r.get('Voided', 'false').lower() != 'true':
                            toast_monthly[m_key]['ns'] += float(r.get('Amount', '0') or '0')
                            toast_monthly[m_key]['t'] += float(r.get('Tip', '0') or '0')
                            toast_monthly[m_key]['o'] += 1
            except Exception as e:
                print(f"  Warning processing orders {dd}: {e}")

        if os.path.exists(item_file):
            try:
                with open(item_file) as f:
                    for r in csv.DictReader(f):
                        if r.get('Void?', 'false').lower() != 'true':
                            toast_monthly[m_key]['i'] += int(float(r.get('Qty', '1') or '1'))
            except Exception as e:
                print(f"  Warning processing items {dd}: {e}")

    existing_months = {x['m'] for x in monthly if x['s'] == 'T'}
    for m_key in sorted(toast_monthly.keys()):
        if m_key not in existing_months:
            v = toast_monthly[m_key]
            monthly.append({'m': m_key, 's': 'T', 'ns': round(v['ns'], 2), 't': round(v['t'], 2), 'o': v['o'], 'i': v['i']})

monthly.sort(key=lambda x: x['m'])

# Merge months from both sources
merged = {}
for x in monthly:
    k = x['m']
    if k in merged:
        merged[k]['ns'] = round(merged[k]['ns'] + x['ns'], 2)
        merged[k]['t'] = round(merged[k]['t'] + x['t'], 2)
        merged[k]['o'] += x['o']
        merged[k]['i'] += x['i']
        if merged[k]['s'] != x['s']:
            merged[k]['s'] = 'B'
    else:
        merged[k] = dict(x)
monthly = list(merged.values())
monthly.sort(key=lambda x: x['m'])
data['monthly'] = monthly
print(f"Monthly: {len(monthly)} months")

# --- Daily data (ALL history) ---
daily = []

# Square daily - ALL dates
sq_daily = SQ + '/daily_sales.csv'
if os.path.exists(sq_daily):
    with open(sq_daily) as f:
        for r in csv.DictReader(f):
            ns = float(r['Net Sales'])
            if ns > 0 or float(r.get('Tips', '0')) > 0:
                daily.append({
                    'd': r['Date'],
                    'ns': ns,
                    't': float(r['Tips']),
                    'o': int(r['Orders']),
                    'i': int(r.get('Items Sold', r.get('Orders', '0')))
                })

# Toast daily from historical
if os.path.isdir(toast_hist):
    for m in sorted(os.listdir(toast_hist)):
        p = os.path.join(toast_hist, m)
        sbd = os.path.join(p, 'Sales by day.csv')
        if os.path.isdir(p) and os.path.exists(sbd):
            try:
                with open(sbd) as f:
                    for r in csv.DictReader(f):
                        raw = r.get('Date', '').strip()
                        if not raw:
                            continue
                        if '/' in raw:
                            parts = raw.split('/')
                            ds = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
                        else:
                            ds = raw
                        ns = round(float(r.get('Net sales', '0') or '0'), 2)
                        if ns > 0:
                            daily.append({
                                'd': ds,
                                'ns': ns,
                                't': 0,
                                'o': int(r.get('Total orders', '0') or '0'),
                                'g': int(r.get('Total guests', '0') or '0')
                            })
            except Exception as e:
                print(f"  Warning processing historical daily {m}: {e}")

# Toast daily from exports
if os.path.isdir(EXPORTS):
    for dd in sorted(os.listdir(EXPORTS)):
        if not dd.isdigit() or len(dd) != 8:
            continue
        ds = dd[:4] + '-' + dd[4:6] + '-' + dd[6:8]
        order_file = os.path.join(EXPORTS, dd, 'OrderDetails.csv')
        if os.path.exists(order_file):
            try:
                day_ns = day_t = 0
                day_o = day_g = 0
                seen_orders = set()
                with open(order_file) as f:
                    for r in csv.DictReader(f):
                        if r.get('Voided', 'false').lower() != 'true':
                            oid = r.get('Order Id', '')
                            if oid not in seen_orders:
                                seen_orders.add(oid)
                                day_o += 1
                                day_g += int(r.get('# of Guests', '0') or '0')
                            day_ns += float(r.get('Amount', '0') or '0')
                            day_t += float(r.get('Tip', '0') or '0')
                if day_ns > 0:
                    daily.append({'d': ds, 'ns': round(day_ns, 2), 't': round(day_t, 2), 'o': day_o, 'g': day_g})
            except Exception as e:
                print(f"  Warning processing daily {dd}: {e}")

daily.sort(key=lambda x: x['d'])
seen = {}
for x in daily:
    seen[x['d']] = x
data['daily'] = list(seen.values())
print(f"Daily: {len(data['daily'])} days")

# --- Items by month (ALL items, with category tags) ---
items = {}

# Square items - ALL items with categories
sq_items = SQ + '/items_by_month.csv'
if os.path.exists(sq_items):
    with open(sq_items) as f:
        for r in csv.DictReader(f):
            m = r['Month']
            if m not in items:
                items[m] = []
            cat = classify_item(r['Item'])
            items[m].append({
                'n': r['Item'],
                'q': int(r['Quantity']),
                'r': round(float(r['Revenue']), 2),
                'c': cat
            })

# Toast items from exports
if os.path.isdir(EXPORTS):
    mi = defaultdict(lambda: defaultdict(lambda: {'q': 0, 'r': 0, 'c': ''}))
    for dd in sorted(os.listdir(EXPORTS)):
        if not dd.isdigit() or len(dd) != 8:
            continue
        item_file = os.path.join(EXPORTS, dd, 'ItemSelectionDetails.csv')
        if os.path.exists(item_file):
            m = dd[:4] + '-' + dd[4:6]
            try:
                with open(item_file) as f:
                    for r in csv.DictReader(f):
                        if r.get('Void?', 'false').lower() != 'true':
                            nm = r.get('Menu Item', 'Unknown').strip()
                            cat = r.get('Sales Category', '').strip() or classify_item(nm)
                            mi[m][nm]['q'] += int(float(r.get('Qty', '1') or '1'))
                            mi[m][nm]['r'] += float(r.get('Net Price', '0') or '0')
                            if cat:
                                mi[m][nm]['c'] = cat
            except Exception as e:
                print(f"  Warning processing items {dd}: {e}")

    for m in mi:
        si = sorted(mi[m].items(), key=lambda x: x[1]['r'], reverse=True)
        items['T_' + m] = [{'n': k, 'q': v['q'], 'r': round(v['r'], 2), 'c': v['c'] or classify_item(k)} for k, v in si]

# Toast items from historical monthly CSVs
HIST = DATA + '/historical'
if os.path.isdir(HIST):
    hi = defaultdict(lambda: defaultdict(lambda: {'q': 0, 'r': 0, 'c': ''}))
    for dd in sorted(os.listdir(HIST)):
        ifile = os.path.join(HIST, dd, 'ItemSelectionDetails.csv')
        if not os.path.exists(ifile):
            continue
        m = dd
        try:
            with open(ifile, newline='') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                for r in reader:
                    voided = r.get('Voided', r.get('Void?', 'false'))
                    if str(voided).strip().lower() in ('true', 'yes'):
                        continue
                    nm = r.get('Menu Item', 'Unknown').strip()
                    if not nm or nm == 'Unknown':
                        continue
                    cat = r.get('Sales Category', '').strip() or classify_item(nm)
                    q = int(float(r.get('Qty', '1') or '1'))
                    net = parse_dollar(r.get('Net', r.get('Net Price', '0')))
                    hi[m][nm]['q'] += q
                    hi[m][nm]['r'] += net
                    if cat:
                        hi[m][nm]['c'] = cat
        except Exception as e:
            print(f"  Warning processing historical items {dd}: {e}")

    for m in hi:
        key = 'T_' + m
        si = sorted(hi[m].items(), key=lambda x: x[1]['r'], reverse=True)
        items[key] = [{'n': k, 'q': v['q'], 'r': round(v['r'], 2), 'c': v['c'] or classify_item(k)} for k, v in si]

# Also update monthly totals from historical ItemSelectionDetails if not already present
if os.path.isdir(HIST):
    existing_months = {x['m'] for x in monthly}
    for dd in sorted(os.listdir(HIST)):
        ifile = os.path.join(HIST, dd, 'ItemSelectionDetails.csv')
        if not os.path.exists(ifile) or dd in existing_months:
            continue
        try:
            orders_seen = set()
            ns = 0; item_count = 0
            with open(ifile, newline='') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                for r in reader:
                    voided = r.get('Voided', r.get('Void?', 'false'))
                    if str(voided).strip().lower() in ('true', 'yes'):
                        continue
                    orders_seen.add(r.get('Order Id', ''))
                    item_count += int(float(r.get('Qty', '1') or '1'))
                    ns += parse_dollar(r.get('Net', r.get('Net Price', '0')))
            monthly.append({'m': dd, 's': 'T', 'ns': round(ns, 2), 't': 0, 'o': len(orders_seen), 'i': item_count})
        except Exception as e:
            print(f"  Warning processing historical monthly {dd}: {e}")
    monthly.sort(key=lambda x: x['m'])

# Toast categories from historical Sales category summary.csv
categories = {}
if os.path.isdir(HIST):
    for dd in sorted(os.listdir(HIST)):
        cat_file = os.path.join(HIST, dd, 'Sales category summary.csv')
        if os.path.exists(cat_file):
            try:
                cats = []
                with open(cat_file) as f:
                    for r in csv.DictReader(f):
                        if r['Sales category'] != 'Total':
                            cats.append({
                                'n': r['Sales category'],
                                'q': int(float(r['Items'])),
                                'r': round(float(r['Net sales']), 2)
                            })
                if cats:
                    categories[dd] = cats
            except Exception as e:
                print(f"  Warning processing categories {dd}: {e}")

# Toast categories from exports
if os.path.isdir(EXPORTS):
    cat_monthly = defaultdict(lambda: defaultdict(lambda: {'q': 0, 'r': 0}))
    for dd in sorted(os.listdir(EXPORTS)):
        if not dd.isdigit() or len(dd) != 8:
            continue
        item_file = os.path.join(EXPORTS, dd, 'ItemSelectionDetails.csv')
        if os.path.exists(item_file):
            m = dd[:4] + '-' + dd[4:6]
            try:
                with open(item_file) as f:
                    for r in csv.DictReader(f):
                        if r.get('Void?', 'false').lower() != 'true':
                            cat = r.get('Sales Category', 'Other').strip()
                            if cat and cat != 'Total':
                                cat_monthly[m][cat]['q'] += int(float(r.get('Qty', '1') or '1'))
                                cat_monthly[m][cat]['r'] += float(r.get('Net Price', '0') or '0')
            except Exception as e:
                pass
    for m in cat_monthly:
        if m not in categories:
            categories[m] = [{'n': k, 'q': v['q'], 'r': round(v['r'], 2)}
                             for k, v in sorted(cat_monthly[m].items(), key=lambda x: x[1]['r'], reverse=True)]

data['categories'] = categories
print(f"Categories: {len(categories)} months")

# Merge items keys: combine Square and Toast into unified months
merged_items = {}
for k, v in items.items():
    canon = k[2:] if k.startswith('T_') else k
    if canon not in merged_items:
        merged_items[canon] = {}
    for it in v:
        nm = it['n']
        if nm in merged_items[canon]:
            merged_items[canon][nm]['q'] += it['q']
            merged_items[canon][nm]['r'] = round(merged_items[canon][nm]['r'] + it['r'], 2)
        else:
            merged_items[canon][nm] = dict(it)

# Convert to sorted lists (ALL items, not just top 20)
final_items = {}
for k, v in merged_items.items():
    si = sorted(v.values(), key=lambda x: x['r'], reverse=True)
    final_items[k] = si

data['items'] = final_items
print(f"Items: {len(final_items)} month-groups, {sum(len(v) for v in final_items.values())} total item records")

# --- Today's data ---
if data['daily']:
    last_date = data['daily'][-1]['d']
    data['todaySales'] = [data['daily'][-1]]

    dd = last_date.replace('-', '')
    item_file = os.path.join(EXPORTS, dd, 'ItemSelectionDetails.csv')
    today_items = []
    if os.path.exists(item_file):
        item_agg = defaultdict(lambda: {'q': 0, 'r': 0, 'c': ''})
        with open(item_file) as f:
            for r in csv.DictReader(f):
                if r.get('Void?', 'false').lower() != 'true':
                    nm = r.get('Menu Item', 'Unknown').strip()
                    item_agg[nm]['q'] += int(float(r.get('Qty', '1') or '1'))
                    item_agg[nm]['r'] += float(r.get('Net Price', '0') or '0')
                    item_agg[nm]['c'] = r.get('Sales Category', '') or classify_item(nm)
        today_items = sorted([{'n': k, 'q': v['q'], 'r': round(v['r'], 2), 'c': v['c']} for k, v in item_agg.items()],
                            key=lambda x: x['r'], reverse=True)
    data['todayItems'] = today_items
else:
    data['todaySales'] = []
    data['todayItems'] = []

# --- Market items ---
market = {}
if os.path.isdir(EXPORTS):
    for dd in sorted(os.listdir(EXPORTS)):
        if not dd.isdigit() or len(dd) != 8:
            continue
        item_file = os.path.join(EXPORTS, dd, 'ItemSelectionDetails.csv')
        if not os.path.exists(item_file):
            continue
        ds = dd[:4] + '-' + dd[4:6] + '-' + dd[6:8]
        di = defaultdict(lambda: {'q': 0, 'net': 0.0, 'gross': 0.0})
        try:
            with open(item_file) as f:
                for r in csv.DictReader(f):
                    if r.get('Void?', 'false').lower() == 'true':
                        continue
                    if r.get('Sales Category', '').strip() == 'Market':
                        nm = r.get('Menu Item', 'Unknown').strip()
                        qt = float(r.get('Qty', '1') or '1')
                        nt = float(r.get('Net Price', '0') or '0')
                        gr = float(r.get('Gross Price', '0') or '0')
                        di[nm]['q'] += qt
                        di[nm]['net'] += nt
                        di[nm]['gross'] += gr
        except Exception as e:
            print(f"  Warning processing market {dd}: {e}")

        if di:
            market[ds] = sorted(
                [{'n': k, 'q': int(v['q']), 'net': round(v['net'], 2), 'gross': round(v['gross'], 2)}
                 for k, v in di.items()],
                key=lambda x: x['net'], reverse=True)

data['market'] = market
print(f"Market: {len(market)} days")

# Write output
with open(OUT, 'w') as f:
    json.dump(data, f, separators=(',', ':'))
print(f"Data written to {OUT} ({os.path.getsize(OUT):,} bytes)")
