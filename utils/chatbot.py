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
    "forgot password": "Click on 'Forgot Password?' on the login page to reset your password.",
    "logout":  "You can log out by clicking on your profile icon and selecting 'Log Out'.",

    # article submission and interaction
    "report": "To report an inappropriate comment or article: For inappropriate article: scroll to the bottom of the article and click on the 'Report' button. For inappropriate comment: click one the ‘…’ to report a comment. ",
    "create": "To create an article, you must have a registered account. Once you logged in, click on the 'Create Your Story' on the right column.",
    "submit article": "Registered users can go to 'Create Your Story', write your stories and upload images, and click on 'Upload Article' once you are done. You can also save your article as draft if you wish to continue writing your story later.",
    "comment": "Registered users can view, comment and reply to others by scrolling to the comment section at the bottom of the article.",
    "report article": "If you find the content of any article inappropriate, click 'Report' under the article to flag it.",
    "report comment": "If you find any inappropriate comments, click 'Report' under the comment to flag it.",
    "view my articles": "To view all your articles, select the menu bar, click on 'View My Articles'. ",
    "view bookmark": "To view your bookmark articles, select the menu bar, click on 'View Bookmark'. ", 
    "bookmark article": "To bookmark an article, click into the article that you would like to save as bookmark and select 'Add Bookmark' to save it for later reading.",
    "view analytics": "To view your analytics, select the menu bar, click on 'View Analytics'. ",
    "edit profile": "To edit your profile details, select the menu bar, click on 'My Profile'. ",

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
