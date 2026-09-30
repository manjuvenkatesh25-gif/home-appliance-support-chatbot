import streamlit as st
import re

# ============================================
# HOME APPLIANCE SUPPORT CHATBOT - CA4
# ============================================

st.set_page_config(
    page_title="Home Appliance Support Chatbot",
    page_icon="🏠",
    layout="centered"
)

# ============================================
# APPLIANCE DATABASE
# ============================================

appliances = [
    {
        "name": "Double Door Refrigerator",
        "brand": "LG",
        "capacity": "260 L",
        "price": 32000,
        "services": ["Installation", "Repair"]
    },
    {
        "name": "Front Load Washing Machine",
        "brand": "Samsung",
        "capacity": "7 kg",
        "price": 28000,
        "services": ["Installation", "Repair"]
    },
    {
        "name": "Split AC",
        "brand": "Voltas",
        "capacity": "1.5 Ton",
        "price": 38000,
        "services": ["Installation", "Service"]
    },
    {
        "name": "Microwave Oven",
        "brand": "IFB",
        "capacity": "25 L",
        "price": 12500,
        "services": ["Repair"]
    },
    {
        "name": "Mixer Grinder",
        "brand": "Philips",
        "capacity": "750 W",
        "price": 4500,
        "services": ["Repair"]
    },
    {
        "name": "LED TV",
        "brand": "Sony",
        "capacity": "55 inch",
        "price": 65000,
        "services": ["Installation", "Repair"]
    }
]

# ============================================
# INTENT DETECTION
# ============================================

def detect_intent(text):

    text = text.lower()

    if any(word in text for word in
           ["hello", "hi", "hey", "good morning", "good afternoon"]):
        return "GREETING"

    if any(word in text for word in
           ["bye", "goodbye", "exit", "quit"]):
        return "GOODBYE"

    if any(word in text for word in
           ["price", "cost", "how much", "rate"]):
        return "PRICE"

    if any(word in text for word in
           ["delivery", "deliver", "shipping"]):
        return "DELIVERY"

    if any(word in text for word in
           ["install", "installation", "setup"]):
        return "INSTALLATION"

    if any(word in text for word in
           ["service", "repair", "technician", "maintenance"]):
        return "SERVICE"

    if any(word in text for word in
           ["specification", "specifications", "specs",
            "capacity", "power", "features"]):
        return "SPECIFICATION"

    if any(word in text for word in
           ["refrigerator", "fridge",
            "washing machine",
            "ac", "air conditioner",
            "microwave",
            "mixer", "mixer grinder",
            "tv", "television"]):
        return "APPLIANCE_SEARCH"

    return "UNKNOWN"


# ============================================
# ENTITY EXTRACTION
# ============================================

def extract_entities(text):

    text = text.lower()
    entities = {}

    # Appliance
    if "refrigerator" in text or "fridge" in text:
        entities["Appliance"] = "Refrigerator"

    elif "washing machine" in text:
        entities["Appliance"] = "Washing Machine"

    elif "air conditioner" in text or " ac" in text:
        entities["Appliance"] = "AC"

    elif "microwave" in text:
        entities["Appliance"] = "Microwave Oven"

    elif "mixer grinder" in text or "mixer" in text:
        entities["Appliance"] = "Mixer Grinder"

    elif "television" in text or " tv" in text:
        entities["Appliance"] = "LED TV"

    # Brand
    brands = ["lg", "samsung", "voltas", "ifb", "philips", "sony"]

    for brand in brands:
        if brand in text:
            entities["Brand"] = brand.title()

    # Capacity
    capacities = ["260 l", "7 kg", "1.5 ton", "25 l", "750 w", "55 inch"]

    for capacity in capacities:
        if capacity in text:
            entities["Capacity"] = capacity

    # Price / Budget
    price_match = re.search(
        r"(?:₹|rs\.?|under|below)\s?(\d+(?:,\d+)?)",
        text
    )

    if price_match:
        entities["Price"] = int(
            price_match.group(1).replace(",", "")
        )

    # Service Type
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

    for appliance in appliances:

        match = True

        if "Appliance" in entities:

            requested = entities["Appliance"].lower()

            if requested == "refrigerator":
                match = "refrigerator" in appliance["name"].lower()

            elif requested == "washing machine":
                match = "washing machine" in appliance["name"].lower()

            elif requested == "ac":
                match = "ac" in appliance["name"].lower()

            elif requested == "microwave oven":
                match = "microwave" in appliance["name"].lower()

            elif requested == "mixer grinder":
                match = "mixer" in appliance["name"].lower()

            elif requested == "led tv":
                match = "tv" in appliance["name"].lower()

        if match and "Brand" in entities:
            match = (
                appliance["brand"].lower()
                == entities["Brand"].lower()
            )

        if match and "Capacity" in entities:
            match = (
                appliance["capacity"].lower()
                == entities["Capacity"].lower()
            )

        if match and "Price" in entities:
            match = (
                appliance["price"]
                <= entities["Price"]
            )

        if match:
            results.append(appliance)

    return results


# ============================================
# CHATBOT RESPONSE
# ============================================

def chatbot_response(user_input):

    intent = detect_intent(user_input)
    entities = extract_entities(user_input)

    # Update conversation memory
    for key, value in entities.items():

        if key in st.session_state.context:
            st.session_state.context[key] = value

    # Combine current and previous information
    search_entities = {}

    for key, value in st.session_state.context.items():

        if value is not None:
            search_entities[key] = value

    # GREETING
    if intent == "GREETING":

        return (
            "Hello! Welcome to the Home Appliance Support Chatbot. "
            "I can help you with appliance search, specifications, "
            "price, delivery, installation and service."
        )

    # GOODBYE
    if intent == "GOODBYE":

        return (
            "Thank you for using the Home Appliance Support Chatbot. "
            "Have a great day!"
        )

    # DELIVERY
    if intent == "DELIVERY":

        appliance = st.session_state.context["Appliance"]

        if appliance:
            return (
                f"Delivery is available for the {appliance}. "
                "Standard delivery usually takes 3–5 working days."
            )

        return (
            "Delivery is available for our appliances. "
            "Please tell me which appliance you are interested in."
        )

    # INSTALLATION
    if intent == "INSTALLATION":

        appliance = st.session_state.context["Appliance"]

        if appliance:
            return (
                f"Installation is available for the {appliance}. "
                "A technician can be scheduled after delivery."
            )

        return (
            "Installation is available for selected appliances. "
            "Please tell me the appliance name."
        )

    # SERVICE
    if intent == "SERVICE":

        appliance = st.session_state.context["Appliance"]
        service_type = st.session_state.context["Service Type"]

        if appliance and service_type:
            return (
                f"{service_type} support is available for the "
                f"{appliance}. Our service team can assist you."
            )

        if appliance:
            return (
                f"Service support is available for the {appliance}. "
                "Please tell me whether you need repair or maintenance."
            )

        return (
            "Sure. Please tell me which appliance requires service."
        )

    # SEARCH / PRICE / SPECIFICATION
    if intent in [
        "APPLIANCE_SEARCH",
        "PRICE",
        "SPECIFICATION"
    ]:

        results = search_appliances(search_entities)

        if results:

            response = ""

            for item in results:

                if intent == "PRICE":

                    response += (
                        f"The price of the {item['name']} "
                        f"by {item['brand']} is "
                        f"₹{item['price']:,}."
                    )

                elif intent == "SPECIFICATION":

                    response += (
                        f"The {item['name']} by {item['brand']} "
                        f"has a capacity of {item['capacity']} "
                        f"and costs ₹{item['price']:,}."
                    )

                else:

                    response += (
                        f"**{item['name']}**\n\n"
                        f"Brand: {item['brand']}\n\n"
                        f"Capacity: {item['capacity']}\n\n"
                        f"Price: ₹{item['price']:,}\n\n"
                        f"Services: {', '.join(item['services'])}"
                    )

            return response

        return (
            "I could not find a matching appliance. "
            "Please provide an appliance name, brand, capacity "
            "or budget."
        )

    return (
        "Sorry, I didn't understand your request. "
        "You can ask me about appliances, specifications, "
        "price, delivery, installation or service."
    )


# ============================================
# STREAMLIT SESSION STATE
# ============================================

if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! Welcome to the Home Appliance Support Chatbot. "
                "How can I help you today?"
            )
        }
    ]

if "context" not in st.session_state:

    st.session_state.context = {
        "Appliance": None,
        "Brand": None,
        "Capacity": None,
        "Price": None,
        "Service Type": None
    }


# ============================================
# USER INTERFACE
# ============================================

st.title("🏠 Home Appliance Support Chatbot")

st.write(
    "Ask me about appliances, specifications, prices, "
    "delivery, installation or service."
)

# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
user_input = st.chat_input(
    "Ask about a home appliance..."
)

if user_input:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Generate response
    response = chatbot_response(user_input)

    # Add bot response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

    # Refresh screen
    st.rerun()
