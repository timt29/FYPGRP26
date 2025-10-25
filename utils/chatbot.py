from flask import jsonify;

FAQ_Responses = {
    # greetings
    "hello": "Hi there! How can I help you today?",
    "hi": "Hi there! How can I help you today?",
    "hey": "Hi there! How can I help you today?",
    "thank you": "You are very welcome! Happy to help anytime!",
    "bye": "Goodbye! Have a great day ahead and hope to see you again soon!",
    # general navigation
    "search": "Enter a keyword into the search bar at the top of the webpage and click on the search button.",
    "share": "To share an article, visit any article page and scroll to the end of the article, look out for the share button and click on it to share the article",
    "navigate": "To browse different topics, click on the categories listed at the top of the homepage.",
    "topics": "To browse different topics, click on the categories listed at the top of the homepage.",
    "homepage": "Click on the EchoPress logo at the top-left corner to return to the homepage.",
    "category": "You can explore articles by category using the navigation bar at the top.",
    # account and log in
    "register": "For all new users, click on the 'Register' button at the top right corner to create a new account.",
    "forgot password": "Click on 'Forgot Psasword?' on the login page to reset your password.",
    "logout":  "You can log out by clicking on your profile icon and selecting 'Log Out'.",
    # article submission and interaction
    "report": "To report a inapporiate user or comment, meowmeow moew moew meow",
    "create": "To create an article, you must have a registered account. Once you logged in, click on the 'Create Your Story' on the right column.",
    "submit article": "Registered users can submit their articles ",
    "comment": "Registered users can view and comment on articles by scrolling to the comment section at the bottom of the article.",
    "report article": "If you find the content of any article inappropriate, click 'Report' under the article to flag it.",
    "report comment": "If you find any inappropriate comments, click 'Report' under the comment to flag it.",
    "bookmark": "To bookmark an article, click on the '...' and select 'Bookmark article' to save it for later reading.",
    # safety rules
    "blocked words": "Our system automatically filters offensive or inappropriate language to protect our readers.",
    "privacy": "EchoPress value all our user's privacy. Your data is securely stored and never shared with third parties.",
    "community guidelines": "Please keep discussions respectful and considerate of others. Offensive or spam content will be removed and reviewed."

}

def getChatbotResponse (user_input):
    user_input = user_input.lower()
    for keyword, answer in FAQ_Responses.items():
        if keyword in user_input:
            return answer
    return "I'm sorry, can't help with that question right now. Please try another question."