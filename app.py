from pprint import pprint
import os
import openai
import requests, json

from flask import Flask, request, render_template, render_template_string, redirect, flash, jsonify, session, g, render_template_string
from forms import StoryForm, ContextForm

from models import db, connect_db, User, Story, Contribution, Guest
from flask_debugtoolbar import DebugToolbarExtension

CURRENT_USER_KEY = 'current_user'
CURRENT_GUEST_KEY = 'current_guest'

openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
# app.debug = True
app.config["SECRET_KEY"] = "mysecurepassword"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///ai_storyteller_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

# app.config['DEBUG'] = True
# app.config['ENV'] = 'development'
# app.config['TESTING'] = True

with app.app_context():
    connect_db(app)
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


def create_guest():
        guest = Guest()
        db.session.add(guest)
        db.session.commit()
        g.guest = guest
        session[CURRENT_GUEST_KEY] = guest.id

@app.before_request
def set_user():
    ''' If logged in, add the current user to global variable '''

    if CURRENT_USER_KEY in session:
        g.user = db.session.get(User,session[CURRENT_USER_KEY])
    else:
        g.user = None


    if CURRENT_GUEST_KEY in session:
        print('YES GUEST IN SESSION')
        g.guest = db.session.get(Guest,session[CURRENT_GUEST_KEY])
    else:
        g.guest = None



@app.route("/", methods=['GET'])
def render_home():

    context_form = ContextForm()
    context_form.genre.choices = [('romance', 'Romance'),('fantasy','Fantasy'),('horror','Horror'),('science fiction','Science Fiction')]
    # if story_form.validate_on_submit():
    #     print('valid submit')
        
    #     session.get('user_id',)

    #     # =======
    #     if session.get('user_session'):
    #         print('session true')
    #         user = User.get(session['user_session'])
    #     else:
    #         print('session false')
    #         guest = Guest()
    #         db.session.add(guest)
    #         db.session.commit()
    #         print(guest.id)
            # session['user_session'] = guest.id
        # =======


        # user = session['user_session'] if session['user_session'] else User()

    #     return redirect("/") # story_starter=story_starter, form=form)
    # else:
    #     CONVERSATION =[{"role": "ai"}]
    #     session['conversation'] = CONVERSATION
    return render_template("app.html",contextForm=context_form)




@app.route('/api/new', methods=['GET'])
def new_story():
    ''' receive the story start request. Should receive a genre and optionally a character name. Should return a the id of a new story. '''

    # TODO  Make a function which randomly generates the starter. Move it to the Context form so genre and starter are included together.
    # story_starter = '''There was once a man with too many arms.'''

    print('START REQUEST', request)

    story_starter = request.args['story_prompt']
    story = Story(genre=request.args['genre'], story_prompt=story_starter,)
    db.session.add(story)
    db.session.commit()
    
    session['story'] = story.serialize() # pass story to session variable


    story_form=StoryForm()
    story_form.story_id.data=story.id


    return(render_template_string('{% include "contribute.html" %}', storyForm=story_form, story_starter=story_starter))


@app.route('/api/contribute', methods=['POST'])
def handle_submission():
    ''' Receive the API call from JS front end. Trigger appropriate functions '''
    
    # TODO: parse arguments, trigger api call to open AI send response back to front end

    if not g.guest:
        create_guest()

    #TODO I should also make sure story_id matches the story id in g.story.id
    text = request.form.get('body')

    story = db.session.get(Story,session['story']['id'])
    story.add_to_story('user',text,g.guest.id)

   
    # GET AI CONTRIBUTION
    ai_contribution = get_ai_contribution(story)

    print(ai_contribution)
    story.add_to_story(ai_contribution['role'],ai_contribution['body'], tokens=ai_contribution['tokens'])


    return jsonify({'role':ai_contribution['role'],'body':ai_contribution['body']})





def get_ai_contribution(story):
    # story = db.session.get(Story,session['story']['id'])

    # construct the prompt
    recent_conversation = story.get_recent()

    if not story.characters:
        character = 'Sally'
    else:
        character = story.characters[0]
    
    system_instructions = f'''
    Assume the role of a cooperative author. We`'re writing a {story.genre} story together. We are taking turns adding to the story one sentence at a time. Your name is AI. My name is User.
    
    Follow these instructions:
    1. Make your response in fewer than 50 words.
    2. If I write an incomplete sentence, you should finish my sentence. Then start another incomplete sentence.

    Example:
    - User: {character} woke up with a huge headache.
    - AI: They knew today would be different.~
    - User: {character} looked everywhere, but couldn`t find
    - AI: anything to eat for breakfast. But while looking, suddenly a giant

    '''
    # 3. Always put your response between quotation marks (" ")

    messages = [
        {'role':'system', 'content':system_instructions},
        *recent_conversation,
        {'role':'system', 'content':system_instructions}
        ]

    # make the call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=1,
        max_tokens=3500
    )

    # Retrieve and clean up the body
    body = response['choices'][0]['message']['content']
    total_tokens = response['usage']['total_tokens']
    # add the contribution to the story
    ''' def add_to_story(self,role,text,guest_id=None,user_id=None): '''
    

    print ({
        'role': 'assistant',
        'body': body,
        'tokens': total_tokens,
    })
    

    #return the response
    return ({
        'role': 'assistant',
        'body': body,
        'tokens': total_tokens,
    })





# @app.route("/send-story/<user_contribution>")
# def send_story(user_contribution):
#     CONVERSATION = session.get('conversaion') if session.get('conversaion') else []
#     CONVERSATION.append({"role": "user", "content": f"{user_contribution}"})
#     print('sending:',user_contribution)
#     #return
   
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
        
    
#         messages=[
#             {"role": "system", "content": story_system_message},
#             *CONVERSATION
#         ],
#         temperature=1,
#         max_tokens=300,
#         top_p=1,
#         frequency_penalty=0.40,
#         presence_penalty=0,
#     )
    
#     ai_story = response['choices'][0]['message']['content']
#     token_usage = response['usage']['total_tokens']
#     CONVERSATION.append({"role": "ai", "content": f"{ai_story}"})
#     session['conversaion'] = CONVERSATION
#     # print(response)
#     print('received:',ai_story,token_usage)
#     pprint(CONVERSATION)
#     return {
#         "ai_story":ai_story,
#         "conversation_length": len(CONVERSATION),
#         "conversation_history": CONVERSATION
#             }
