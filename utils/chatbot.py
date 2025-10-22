from flask import jsonify;

FAQ_Responses = {
    "hello": "Hi there! How can I help you today?",
    "search": "Enter a keyword into the search bar at the top of the webpage and click on the search button.",

    "how to create article": "To create an article, you must have a registered account. Once you logged in, click on the 'Create Your Story' on the right column.",
    "how to share article": "To share an article, visit any article page and scroll to the end of the article, look out for the share button and click on it to share the article",
    "how to register": "For all new users, kindly click on the orange 'register' button at the top right corner of the navigation bar.",
    "how to search for article": "Enter a keyword into the search bar at the top of the webpage and click on the search button."
}

def getChatbotResponse (user_input):
    user_input = user_input.lower()
    for keyword, answer in FAQ_Responses.items():
        if keyword in user_input:
            return jsonify({"response": answer})
    return jsonify({"response": "I'm sorry, can't help with that question right now. Please try another question."})