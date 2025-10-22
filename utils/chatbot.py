from flask import jsonify;

FAQ_Responses = {
    "hello": "Hi there! What can I help you with today?",
    "how to create article": "To create an article, you must have a registered account. Once you logged in, click on the 'Create Your Story' on the right column.",
    "how to share article": "To share an article, visit any article page and scroll to the end of the article, look out for the share button and click on it to share the article"
}

def getChatbotResponse (user_input):
    user_input = user_input.lower()
    for question, answer in FAQ_Responses.items():
        if question in user_input:
            return jsonify({"response": answer})
    return jsonify({"response": "I'm sorry, can't help with that question right now. Please try another question."})