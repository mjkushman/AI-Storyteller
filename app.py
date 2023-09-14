from pprint import pprint
import os
import openai
from flask import Flask, request, render_template, redirect, flash, jsonify, session
from forms import StoryForm
from models import db, User, Story, Context, connect_db
from flask_debugtoolbar import DebugToolbarExtension

openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = "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"


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "mysecurepassword"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///ai_storyteller_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['TESTING'] = True

connect_db(app)
with app.app_context():
    db.create_all()

"""
====================================MAKE CALL TO AI ==============================
"""
# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "What is the capitol of California?"},
#     ],
#     temperature=1,
#     max_tokens=210,
#     top_p=1,
#     frequency_penalty=0.40,
#     presence_penalty=0,
#     stream=True,  # this time, we set stream=True
# )

# collected_chunks = []
# collected_messages = []


# for chunk in response:

#     collected_chunks.append(chunk)  # save the event response
#     chunk_message = chunk["choices"][0]["delta"]  # extract the message
#     collected_messages.append(chunk_message)  # save the message

#     trimmed_message_chuck = chunk_message.get('content','').strip()
#     print(trimmed_message_chuck) #successfully prints one word at a time

# full_reply_content = ''.join([m.get('content', '') for m in collected_messages])

# ==================================================================

story_system_message = """
We're writing a story together. We each take a turn adding a fragment of a sentence.
Instructions:
1) Respond in 30 words or less

2) Finish each others sentences with the following pattern:

3) We take turns finishing each others sentences with the following pattern:
3 a) I will write an incomplete sentence, which you must finish.
3 b) You will write an incomplete sentence, which I must finish

Below is an example:

I say: 
Once upon a time, there was a very large
You respond: 
cat who lived in a house. But the cat grew so large that
"""


starter_system_message = """
We're writing a light-hearted story together. Respond in less than 25 words.

"""

STARTER_PROMPTS = [
    {"role": "system", "content": 'Start a story for me to carry on. Establish at least one character, a setting, and an objective for the character.'},
    {"role": "system", "content": 'In under 30 words, write an unfinished sentence for me to finish.'},
    ]


@app.route("/", methods=['GET','POST'])
def render_home():
    # session.clear()
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
        
        
    #     messages=[
    #         {"role": "system", "content": starter_system_message},
    #         *STARTER_PROMPTS
    #     ],
    #     temperature=1,
    #     max_tokens=300,
    #     top_p=1,
    #     frequency_penalty=0.40,
    #     presence_penalty=0,
    # )
    # story_starter = response['choices'][0]['message']['content']
    
    # session['user_session'] = user.id
    form = StoryForm()
    story_starter = '''There was once a man with too many arms.'''
    print('starter: ',story_starter)
    
    if form.validate_on_submit():
        print('valid submit')
        if session.get('user_session'):
            print('session true')
            user = User.get(session['user_session'])
        else:
            print('session false')
            user = User()
            session['user_session'] = user.id
        # user = session['user_session'] if session['user_session'] else User()

        return redirect ("/") # story_starter=story_starter, form=form)
    else:
        CONVERSATION =[{"role": "ai", "content":story_starter}]
        session['conversation'] = CONVERSATION
        return render_template("app.html",story_starter=story_starter,form=form)


@app.route("/send-story/<user_contribution>")
def send_story(user_contribution):
    CONVERSATION = session.get('conversaion') if session.get('conversaion') else []
    CONVERSATION.append({"role": "user", "content": f"{user_contribution}"})
    print('sending:',user_contribution)
    #return
   
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        
    
        messages=[
            {"role": "system", "content": story_system_message},
            *CONVERSATION
        ],
        temperature=1,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0.40,
        presence_penalty=0,
    )
    
    ai_story = response['choices'][0]['message']['content']
    token_usage = response['usage']['total_tokens']
    CONVERSATION.append({"role": "ai", "content": f"{ai_story}"})
    session['conversaion'] = CONVERSATION
    # print(response)
    print('received:',ai_story,token_usage)
    pprint(CONVERSATION)
    return {
        "ai_story":ai_story,
        "conversation_length": len(CONVERSATION),
        "conversation_history": CONVERSATION
            }
