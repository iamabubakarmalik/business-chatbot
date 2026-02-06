print("🤖 AI Business Chatbot (FREE MODE) Ready!")

customer_name = ""
customer_need = ""

def ai_reply(user):
    global customer_name, customer_need
    user = user.lower()

    if "my name is" in user:
        customer_name = user.replace("my name is", "").strip().title()
        return f"Nice to meet you, {customer_name}! What kind of business do you run?"

    if any(word in user for word in ["shop", "store", "ecommerce", "online"]):
        customer_need = "sales"
        return "Great! This chatbot can help increase your online sales and answer customer queries 24/7."

    if any(word in user for word in ["service", "agency", "company"]):
        customer_need = "support"
        return "Perfect. This chatbot can reduce support workload and respond instantly to clients."

    if any(word in user for word in ["price", "pricing", "cost"]):
        if customer_name:
            return f"{customer_name}, our plans start from $29/month depending on your business size."
        return "Our plans start from $29/month depending on your business size."

    if any(word in user for word in ["contact", "email"]):
        return "Please share your email, and our team will reach out shortly."

    return "Tell me about your business so I can suggest the best chatbot setup 🙂"


while True:
    user = input("Customer: ")

    if user.lower() == "bye":
        print("Bot: Thanks for visiting! 👋")
        break

    print("Bot:", ai_reply(user))
