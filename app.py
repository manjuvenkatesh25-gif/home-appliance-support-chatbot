import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# ============================================
# HOME APPLIANCE SUPPORT CHATBOT - CA4
# ============================================

st.set_page_config(
    page_title="Home Appliance Support Chatbot",
    page_icon="🏠",
    layout="wide",
)

# ============================================
# APPLIANCE DATABASE
# ============================================

appliances = [
    {"name": "Double Door Refrigerator", "type": "Refrigerator", "icon": "fridge",
     "brand": "LG", "capacity": "260 L", "price": 32000,
     "services": ["Installation", "Repair"], "colors": ((30, 60, 114), (66, 133, 244))},
    {"name": "Front Load Washing Machine", "type": "Washing Machine", "icon": "washer",
     "brand": "Samsung", "capacity": "7 kg", "price": 28000,
     "services": ["Installation", "Repair"], "colors": ((0, 105, 148), (0, 168, 150))},
    {"name": "Split AC", "type": "AC", "icon": "ac",
     "brand": "Voltas", "capacity": "1.5 Ton", "price": 38000,
     "services": ["Installation", "Service"], "colors": ((106, 17, 203), (37, 117, 252))},
    {"name": "Microwave Oven", "type": "Microwave Oven", "icon": "microwave",
     "brand": "IFB", "capacity": "25 L", "price": 12500,
     "services": ["Repair"], "colors": ((200, 80, 60), (255, 150, 90))},
    {"name": "Mixer Grinder", "type": "Mixer Grinder", "icon": "mixer",
     "brand": "Philips", "capacity": "750 W", "price": 4500,
     "services": ["Repair"], "colors": ((20, 120, 80), (90, 190, 120))},
    {"name": "LED TV", "type": "LED TV", "icon": "tv",
     "brand": "Sony", "capacity": "55 inch", "price": 65000,
     "services": ["Installation", "Repair"], "colors": ((40, 40, 60), (110, 90, 170))},
]

TYPES = [a["type"] for a in appliances]
BRANDS = sorted({a["brand"] for a in appliances})
SERVICE_TYPES = ["Installation", "Repair", "Service", "Maintenance"]

# ============================================
# IMAGE GENERATION (no internet / files needed)
# ============================================


def _font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _gradient(width, height, c1, c2):
    img = Image.new("RGB", (width, height))
    px = img.load()
    for y in range(height):
        for x in range(width):
            t = (x / width * 0.6) + (y / height * 0.4)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return img


def _draw_icon(d, kind, cx, cy, s):
    """Draws a simple white appliance icon centred at (cx, cy), size s."""
    w = (255, 255, 255, 235)
    dark = (0, 0, 0, 90)
    if kind == "fridge":
        d.rounded_rectangle([cx - s * .3, cy - s * .5, cx + s * .3, cy + s * .5], 14, outline=w, width=6)
        d.line([cx - s * .3, cy - s * .1, cx + s * .3, cy - s * .1], fill=w, width=5)
        d.line([cx + s * .18, cy - s * .35, cx + s * .18, cy - s * .2], fill=w, width=6)
        d.line([cx + s * .18, cy + s * .02, cx + s * .18, cy + s * .25], fill=w, width=6)
    elif kind == "washer":
        d.rounded_rectangle([cx - s * .4, cy - s * .5, cx + s * .4, cy + s * .5], 14, outline=w, width=6)
        d.ellipse([cx - s * .25, cy - s * .2, cx + s * .25, cy + s * .3], outline=w, width=6)
        d.ellipse([cx - s * .1, cy - s * .05, cx + s * .1, cy + s * .15], fill=dark)
        d.ellipse([cx - s * .32, cy - s * .42, cx - s * .24, cy - s * .34], fill=w)
    elif kind == "ac":
        d.rounded_rectangle([cx - s * .55, cy - s * .25, cx + s * .55, cy + s * .15], 12, outline=w, width=6)
        for i in range(3):
            d.line([cx - s * .4, cy + s * .02 + i * 0 , cx + s * .4, cy + s * .02], fill=w, width=4)
        for i in range(-2, 3):
            d.line([cx + i * s * .18, cy + s * .22, cx + i * s * .22, cy + s * .5], fill=w, width=4)
    elif kind == "microwave":
        d.rounded_rectangle([cx - s * .5, cy - s * .32, cx + s * .5, cy + s * .32], 12, outline=w, width=6)
        d.rectangle([cx - s * .4, cy - s * .22, cx + s * .12, cy + s * .22], outline=w, width=5)
        for i in range(3):
            d.ellipse([cx + s * .26, cy - s * .2 + i * s * .15, cx + s * .36, cy - s * .1 + i * s * .15], fill=w)
    elif kind == "mixer":
        d.polygon([(cx - s * .25, cy - s * .5), (cx + s * .25, cy - s * .5),
                   (cx + s * .15, cy + s * .1), (cx - s * .15, cy + s * .1)], outline=w, width=6)
        d.rounded_rectangle([cx - s * .3, cy + s * .1, cx + s * .3, cy + s * .5], 10, outline=w, width=6)
        d.ellipse([cx - s * .05, cy + s * .24, cx + s * .05, cy + s * .34], fill=w)
    elif kind == "tv":
        d.rounded_rectangle([cx - s * .55, cy - s * .38, cx + s * .55, cy + s * .25], 10, outline=w, width=6)
        d.line([cx - s * .2, cy + s * .42, cx + s * .2, cy + s * .42], fill=w, width=6)
        d.line([cx, cy + s * .25, cx, cy + s * .42], fill=w, width=6)
    elif kind == "home":
        d.polygon([(cx - s * .5, cy), (cx, cy - s * .5), (cx + s * .5, cy)], outline=w, width=6)
        d.rectangle([cx - s * .35, cy, cx + s * .35, cy + s * .45], outline=w, width=6)
        d.rectangle([cx - s * .08, cy + s * .15, cx + s * .08, cy + s * .45], fill=w)


@st.cache_data(show_spinner=False)
def make_card(kind, c1, c2, title="", subtitle="", width=600, height=300):
    img = _gradient(width, height, c1, c2)
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse([width * .55, -height * .4, width * 1.25, height * .6], fill=(255, 255, 255, 25))
    _draw_icon(d, kind, width * .5, height * (.42 if title else .5), min(width, height) * .62)
    if title:
        d.text((24, height - 70), title, font=_font(30), fill=(255, 255, 255, 255))
    if subtitle:
        d.text((26, height - 34), subtitle, font=_font(18), fill=(255, 255, 255, 215))
    return img


@st.cache_data(show_spinner=False)
def make_hero(width=1400, height=300):
    img = _gradient(width, height, (30, 60, 114), (106, 17, 203))
    d = ImageDraw.Draw(img, "RGBA")
    kinds = ["fridge", "washer", "ac", "microwave", "mixer", "tv"]
    step = width * .5 / len(kinds)
    for i, k in enumerate(kinds):
        d.ellipse([width * .48 + i * step - 5, height * .5 - 5, width * .48 + i * step + 5, height * .5 + 5],
                  fill=(255, 255, 255, 0))
        _draw_icon(d, k, width * .56 + i * step * .96, height * .5, height * .42)
    d.text((40, 70), "Home Appliance Support", font=_font(54), fill=(255, 255, 255, 255))
    d.text((42, 140), "Search • Compare • Book service • Chat", font=_font(26), fill=(255, 255, 255, 220))
    return img


# ============================================
# INTENT DETECTION
# ============================================


def has_word(text, words):
    return any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)


def detect_intent(text):
    text = text.lower()

    if has_word(text, ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return "GREETING"
    if has_word(text, ["bye", "goodbye", "exit", "quit"]):
        return "GOODBYE"
    if has_word(text, ["price", "cost", "how much", "rate"]):
        return "PRICE"
    if has_word(text, ["delivery", "deliver", "shipping"]):
        return "DELIVERY"
    if has_word(text, ["install", "installation", "setup"]):
        return "INSTALLATION"
    if has_word(text, ["service", "repair", "technician", "maintenance"]):
        return "SERVICE"
    if has_word(text, ["emi", "installment", "installments", "instalment"]):
        return "EMI"
    if has_word(text, ["specification", "specifications", "specs",
                       "capacity", "power", "features"]):
        return "SPECIFICATION"
    if has_word(text, ["refrigerator", "fridge", "washing machine", "ac",
                       "air conditioner", "microwave", "mixer", "mixer grinder",
                       "tv", "television", "show", "list", "all"]):
        return "APPLIANCE_SEARCH"
    return "UNKNOWN"


# ============================================
# ENTITY EXTRACTION
# ============================================


def extract_entities(text):
    text = text.lower()
    entities = {}

    if has_word(text, ["refrigerator", "fridge"]):
        entities["Appliance"] = "Refrigerator"
    elif "washing machine" in text:
        entities["Appliance"] = "Washing Machine"
    elif has_word(text, ["air conditioner", "ac"]):
        entities["Appliance"] = "AC"
    elif "microwave" in text:
        entities["Appliance"] = "Microwave Oven"
    elif has_word(text, ["mixer grinder", "mixer"]):
        entities["Appliance"] = "Mixer Grinder"
    elif has_word(text, ["television", "tv", "led tv"]):
        entities["Appliance"] = "LED TV"

    for brand in BRANDS:
        if has_word(text, [brand.lower()]):
            entities["Brand"] = brand

    for capacity in ["260 l", "7 kg", "1.5 ton", "25 l", "750 w", "55 inch"]:
        if capacity in text:
            entities["Capacity"] = capacity

    price_match = re.search(r"(?:₹|rs\.?|inr|under|below|within)\s?(\d+(?:,\d+)*)", text)
    if price_match:
        entities["Price"] = int(price_match.group(1).replace(",", ""))

    if "repair" in text:
        entities["Service Type"] = "Repair"
    elif "installation" in text or "install" in text:
        entities["Service Type"] = "Installation"
    elif "maintenance" in text:
        entities["Service Type"] = "Maintenance"
    elif "service" in text:
        entities["Service Type"] = "Service"

    return entities


# ============================================
# SEARCH DATABASE
# ============================================


def search_appliances(entities):
    results = []
    for a in appliances:
        if "Appliance" in entities and a["type"].lower() != entities["Appliance"].lower():
            continue
        if "Brand" in entities and a["brand"].lower() != entities["Brand"].lower():
            continue
        if "Capacity" in entities and a["capacity"].lower() != entities["Capacity"].lower():
            continue
        if "Price" in entities and a["price"] > entities["Price"]:
            continue
        results.append(a)
    return results


def emi(principal, annual_rate, months):
    if months <= 0:
        return 0
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


# ============================================
# CHATBOT RESPONSE
# ============================================


def chatbot_response(user_input):
    ctx = st.session_state.context
    intent = detect_intent(user_input)
    entities = extract_entities(user_input)

    # A newly mentioned appliance starts a fresh search: clear stale brand/capacity/price
    if "Appliance" in entities and entities["Appliance"] != ctx.get("Appliance"):
        for k in ("Brand", "Capacity", "Price"):
            if k not in entities:
                ctx[k] = None

    for key, value in entities.items():
        ctx[key] = value

    search_entities = {k: v for k, v in ctx.items() if v is not None and k != "Service Type"}

    if intent == "GREETING":
        return ("Hello! Welcome to the Home Appliance Support Chatbot. "
                "I can help with appliance search, specifications, price, "
                "EMI, delivery, installation and service.")

    if intent == "GOODBYE":
        return "Thank you for using the Home Appliance Support Chatbot. Have a great day!"

    appliance = ctx.get("Appliance")

    if intent == "DELIVERY":
        if appliance:
            return (f"Delivery is available for the {appliance}. "
                    "Standard delivery usually takes 3–5 working days.")
        return ("Delivery is available for our appliances. "
                "Please tell me which appliance you are interested in.")

    if intent == "INSTALLATION":
        if appliance:
            offered = [a for a in appliances if a["type"] == appliance and "Installation" in a["services"]]
            if offered:
                return (f"Installation is available for the {appliance}. "
                        "A technician can be scheduled after delivery.")
            return f"Installation is not listed for the {appliance}."
        return "Installation is available for selected appliances. Please tell me the appliance name."

    if intent == "SERVICE":
        service_type = ctx.get("Service Type")
        if appliance and service_type:
            return (f"{service_type} support is available for the {appliance}. "
                    "Use the **Book a Service** tab to schedule a visit.")
        if appliance:
            return (f"Service support is available for the {appliance}. "
                    "Please tell me whether you need repair or maintenance.")
        return "Sure. Please tell me which appliance requires service."

    if intent == "EMI":
        results = search_appliances(search_entities)
        if len(results) == 1:
            item = results[0]
            m = emi(item["price"], 10.5, 12)
            return (f"For the {item['name']} (₹{item['price']:,}), a 12-month EMI at a "
                    f"sample 10.5% rate is about ₹{m:,.0f}/month. "
                    "Try the **EMI Calculator** tab for other options.")
        return "Tell me which appliance you want an EMI for, or use the **EMI Calculator** tab."

    if intent in ["APPLIANCE_SEARCH", "PRICE", "SPECIFICATION"]:
        results = search_appliances(search_entities)
        if results:
            parts = []
            for item in results:
                if intent == "PRICE":
                    parts.append(f"The price of the {item['name']} by {item['brand']} is ₹{item['price']:,}.")
                elif intent == "SPECIFICATION":
                    parts.append(f"The {item['name']} by {item['brand']} has a capacity of "
                                 f"{item['capacity']} and costs ₹{item['price']:,}.")
                else:
                    parts.append(f"**{item['name']}**\n\nBrand: {item['brand']}\n\n"
                                 f"Capacity: {item['capacity']}\n\nPrice: ₹{item['price']:,}\n\n"
                                 f"Services: {', '.join(item['services'])}")
            return "\n\n---\n\n".join(parts)
        return ("I could not find a matching appliance. Please provide an appliance "
                "name, brand, capacity or budget.")

    return ("Sorry, I didn't understand your request. You can ask me about appliances, "
            "specifications, price, EMI, delivery, installation or service.")


# ============================================
# SESSION STATE
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! Welcome to the Home Appliance Support Chatbot. How can I help you today?",
    }]

if "context" not in st.session_state:
    st.session_state.context = {
        "Appliance": None, "Brand": None, "Capacity": None,
        "Price": None, "Service Type": None,
    }

if "bookings" not in st.session_state:
    st.session_state.bookings = []

# ============================================
# SIDEBAR – INPUT BOXES / FILTERS
# ============================================

with st.sidebar:
    st.header("🔎 Find an appliance")
    f_type = st.multiselect("Appliance type", TYPES)
    f_brand = st.multiselect("Brand", BRANDS)
    f_budget = st.slider("Max budget (₹)", 3000, 70000, 70000, step=1000)
    f_service = st.selectbox("Service offered", ["Any", "Installation", "Repair", "Service"])
    f_text = st.text_input("Search by name", placeholder="e.g. split, front load")

    st.divider()
    ctx = st.session_state.context
    st.subheader("Chat memory")
    active = {k: v for k, v in ctx.items() if v is not None}
    if active:
        for k, v in active.items():
            st.write(f"**{k}:** {v}")
    else:
        st.caption("Nothing remembered yet.")

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = st.session_state.messages[:1]
        st.session_state.context = {k: None for k in st.session_state.context}
        st.rerun()

filtered = [
    a for a in appliances
    if (not f_type or a["type"] in f_type)
    and (not f_brand or a["brand"] in f_brand)
    and a["price"] <= f_budget
    and (f_service == "Any" or f_service in a["services"])
    and (not f_text or f_text.lower() in a["name"].lower())
]

# ============================================
# HEADER
# ============================================

st.image(make_hero(), use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Appliances", len(appliances))
m2.metric("Brands", len(BRANDS))
m3.metric("Starting at", f"₹{min(a['price'] for a in appliances):,}")
m4.metric("Matches your filters", len(filtered))

tab_chat, tab_browse, tab_book, tab_emi, tab_about = st.tabs(
    ["💬 Chat", "🛒 Browse & Compare", "🔧 Book a Service", "💳 EMI Calculator", "ℹ️ About"]
)

# ============================================
# TAB 1 – CHAT
# ============================================

with tab_chat:
    st.write("Ask me about appliances, specifications, prices, EMI, delivery, installation or service.")

    quick = {
        "📺 Show all": "Show all appliances",
        "💰 Under ₹30,000": "Show appliances under 30000",
        "🚚 Delivery": "Tell me about delivery",
        "🔧 Repair": "I need repair",
    }
    clicked = None
    qcols = st.columns(len(quick))
    for col, (label, text) in zip(qcols, quick.items()):
        if col.button(label, use_container_width=True):
            clicked = text

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask about a home appliance...") or clicked

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": chatbot_response(user_input)})
        st.rerun()

# ============================================
# TAB 2 – BROWSE & COMPARE
# ============================================

with tab_browse:
    st.subheader(f"{len(filtered)} appliance(s) match")

    if not filtered:
        st.warning("No appliances match. Try raising the budget or clearing filters.")

    cols = st.columns(3)
    for i, a in enumerate(filtered):
        with cols[i % 3]:
            with st.container(border=True):
                st.image(make_card(a["icon"], a["colors"][0], a["colors"][1],
                                   a["name"][:28], f"{a['brand']} • {a['capacity']}"),
                         use_container_width=True)
                st.markdown(f"**₹{a['price']:,}**")
                st.caption("Services: " + ", ".join(a["services"]))

    if filtered:
        st.subheader("Price comparison")
        df = pd.DataFrame({
            "Appliance": [a["name"] for a in filtered],
            "Price (₹)": [a["price"] for a in filtered],
        }).set_index("Appliance")
        st.bar_chart(df)

        st.subheader("Compare side by side")
        picks = st.multiselect("Pick 2–3 appliances", [a["name"] for a in filtered],
                               default=[a["name"] for a in filtered][:2])
        if picks:
            comp = pd.DataFrame([
                {"Appliance": a["name"], "Brand": a["brand"], "Capacity": a["capacity"],
                 "Price": f"₹{a['price']:,}", "Services": ", ".join(a["services"])}
                for a in filtered if a["name"] in picks
            ]).set_index("Appliance").T
            st.dataframe(comp, use_container_width=True)

# ============================================
# TAB 3 – BOOK A SERVICE
# ============================================

with tab_book:
    st.subheader("Book a technician visit")
    st.caption("Demo form — entries are kept in this session only.")

    with st.form("service_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full name")
        phone = c2.text_input("Phone number (10 digits)")
        pincode = c1.text_input("Pincode (6 digits)")
        b_appliance = c2.selectbox("Appliance", [a["name"] for a in appliances])
        b_service = c1.selectbox("Service type", SERVICE_TYPES)
        b_date = c2.date_input("Preferred date", date.today() + timedelta(days=2),
                               min_value=date.today())
        b_slot = c1.radio("Time slot", ["9 AM – 12 PM", "12 PM – 3 PM", "3 PM – 6 PM"], horizontal=True)
        issue = st.text_area("Describe the issue (optional)",
                             placeholder="e.g. Fridge is not cooling properly")
        submit = st.form_submit_button("Book service")

    if submit:
        chosen = next(a for a in appliances if a["name"] == b_appliance)
        if not name.strip():
            st.error("Please enter your name.")
        elif not re.fullmatch(r"[6-9]\d{9}", phone.strip()):
            st.error("Please enter a valid 10-digit Indian mobile number.")
        elif not re.fullmatch(r"\d{6}", pincode.strip()):
            st.error("Please enter a valid 6-digit pincode.")
        elif b_service in ("Installation", "Repair", "Service") and b_service not in chosen["services"]:
            st.warning(f"{b_service} is not listed for the {b_appliance}. "
                       f"Available: {', '.join(chosen['services'])}.")
        else:
            st.session_state.bookings.append({
                "Name": name, "Phone": phone, "Pincode": pincode,
                "Appliance": b_appliance, "Service": b_service,
                "Date": str(b_date), "Slot": b_slot, "Issue": issue,
            })
            st.success(f"Thanks {name}! {b_service} for the {b_appliance} is booked "
                       f"on {b_date:%d %b %Y}, {b_slot}.")

    if st.session_state.bookings:
        st.subheader("Bookings this session")
        st.dataframe(pd.DataFrame(st.session_state.bookings), use_container_width=True)

# ============================================
# TAB 4 – EMI CALCULATOR
# ============================================

with tab_emi:
    st.subheader("Plan your purchase")
    e_item = st.selectbox("Appliance", [a["name"] for a in appliances], key="emi_item")
    price = next(a["price"] for a in appliances if a["name"] == e_item)

    c1, c2, c3 = st.columns(3)
    down = c1.number_input("Down payment (₹)", 0, price, int(price * 0.1), step=500)
    rate = c2.slider("Interest rate (% per year)", 0.0, 24.0, 10.5, step=0.5)
    months = c3.select_slider("Tenure (months)", options=[3, 6, 9, 12, 18, 24, 36], value=12)

    principal = price - down
    monthly = emi(principal, rate, months)
    total_pay = monthly * months + down

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Price", f"₹{price:,}")
    r2.metric("Loan amount", f"₹{principal:,}")
    r3.metric("Monthly EMI", f"₹{monthly:,.0f}")
    r4.metric("Total payable", f"₹{total_pay:,.0f}")

    st.caption(f"Total interest: ₹{total_pay - price:,.0f}")

    balance = principal
    rows = []
    mr = rate / 12 / 100
    for m in range(1, months + 1):
        interest = balance * mr
        balance = max(balance - (monthly - interest), 0)
        rows.append({"Month": m, "Balance (₹)": round(balance)})
    if rows:
        st.line_chart(pd.DataFrame(rows).set_index("Month"))

# ============================================
# TAB 5 – ABOUT
# ============================================

with tab_about:
    st.subheader("What this app does")
    a1, a2, a3 = st.columns(3)
    cards = [
        ("tv", (30, 60, 114), (66, 133, 244), "Ask", "Chat in plain English",
         "Intent detection and entity extraction understand the appliance, brand, "
         "capacity, budget and service type, and remember them across messages."),
        ("washer", (0, 105, 148), (0, 168, 150), "Compare", "Filter & compare",
         "Use the sidebar filters, view price charts and compare appliances side by side."),
        ("home", (255, 126, 95), (254, 180, 123), "Book", "Service & EMI",
         "Book a technician visit with validated inputs and plan payments with the EMI calculator."),
    ]
    for col, (icon, c1_, c2_, t, s, desc) in zip((a1, a2, a3), cards):
        with col:
            st.image(make_card(icon, c1_, c2_, t, s, 600, 260), use_container_width=True)
            st.write(desc)

    st.markdown(
        "**Tech:** Streamlit, rule-based NLP (intents + entities with regex), "
        "pandas, Pillow-generated graphics.\n\n"
        "**Disclaimer:** Products, prices, EMI rates and policies are fictional demo data."
    )
