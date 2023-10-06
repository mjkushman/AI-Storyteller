import os
import openai
import requests, json

from flask import (
    Flask,
    request,
    render_template,
    render_template_string,
    redirect,
    flash,
    jsonify,
    session,
    g,
    render_template_string,
    url_for,
)
from forms import StoryForm, ContextForm, SignUpForm, SignInForm
from sqlalchemy.exc import IntegrityError


from models import db, connect_db, User, Story, Contribution, AnonStory
from flask_debugtoolbar import DebugToolbarExtension

CURRENT_USER_KEY = "current_user"
STORY_KEY = 'story'

openai.api_key = os.getenv("OPENAI_API_KEY")


app = Flask(__name__)
# app.debug = True
app.config["SECRET_KEY"] = "mysecurepassword"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///ai_storyteller_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

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


def do_login(user):
    """Log in user."""
    session[CURRENT_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]
    if STORY_KEY in session:
        del session[STORY_KEY]

def set_story_session(story):
    db.session = story.id

def clear_story():
    if STORY_KEY in session:
        del session[STORY_KEY]


@app.before_request
def set_user():
    """If logged in, add the current user to global variable"""

    if CURRENT_USER_KEY in session:
        g.user = db.session.get(User, session[CURRENT_USER_KEY])
    else:
        g.user = None
    
    if STORY_KEY in session:
        # User has a story in session. It's either an authenticated story or anonstory
        # print('SESSION[STORY_KEY] BEFORE REQUEST',session[STORY_KEY])
        story_data = json.loads(session[STORY_KEY])
        if 'id' in story_data['context']:
            # if story has an id, it is authenticated
            g.story = db.session.get(Story, story_data['context']['id'])
        else:
            # story does not have an id and is not authenticated.
            story_data = json.loads(session[STORY_KEY])
            
            g.story = AnonStory(**story_data['context'])
            g.story.contributions = story_data['contributions']
            
    else:
        # No story in session or local storage
        g.story = None

    # print('current g.story',g.story)



# PAGE ROUTES
@app.route("/", methods=["GET", "POST"])
def render_home():
    user = g.user #evaluates to a user object or None
    story = g.story
    
    context_form = ContextForm()

    context_form.genre.choices = [
        ("Adventure", "Adventure"),
        ("Amateur Sleuth", "Amateur Sleuth"),
        ("Children's", "Children's"),
        ("Comedy", "Comedy"),
        ("Conspiracy", "Conspiracy"),
        ("Crime Drama", "Crime Drama"),
        ("Disaster", "Disaster"),
        ("Fantasy", "Fantasy"),
        ("Ghost", "Ghost"),
        ("Gothic", "Gothic"),
        ("High Fantasy", "High Fantasy"),
        ("Historical Fiction", "Historical Fiction"),
        ("Horror", "Horror"),
        ("Mystery", "Mystery"),
        ("Psychological Thriller", "Psychological Thriller"),
        ("Revenge Thriller", "Revenge Thriller"),
        ("Romance", "Romance"),
        ("Science Fiction", "Science Fiction"),
        ("Steampunk Sci-Fi", "Steampunk Sci-Fi"),
        ("Suspence", "Suspence / Thriller"),
        ("Wereworlf Romance", "Wereworlf Romance"),
        ("Western", "Western"),
        ("Young Adult", "Young Adult"),
        ]


    if story:
        # do this if there's already a story in progress
        context_display='d-none'
        contribution_display='d-block'
        genre=story.genre
        story_prompt=story.story_prompt
        

        contributions = story.contributions

        story_form = StoryForm(story_prompt=story_prompt, story_genre=genre)
        return render_template('contribute.html', user=user, story=story, story_form=story_form, contributions=contributions, contextForm=context_form,context_display=context_display, contribution_display=contribution_display)


    else:
        # Do this if there is not already a story in progress
        print('entering ELSE for home')
        context_display='d-block'
        contribution_display='d-none'


        return render_template("contribute.html", contextForm=context_form,user=user, story_form=StoryForm(),context_display=context_display, contribution_display=contribution_display)


@app.route('/sign-up', methods=['GET','POST'])
def render_signup():
    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                email=form.email.data,
                username=form.username.data,
                password=form.password.data
                )
            db.session.commit()
        except IntegrityError: 
            flash("Username already taken",'danger')
            return render_template('signin.html',form=form)
        
        do_login(user)
        
        flash(f'Account created. Welcome {user.username}!', 'success')
        return redirect('/')
        
    return render_template('signup.html', form=form)




@app.route('/sign-in', methods=['GET','POST'])
def render_sign_in():
    story = g.story
    form = SignInForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data, form.password.data)
        # print('=======SIGN IN====== VALIDATED')
        # print(user)
        # print(user.id)

        if user:
            do_login(user)
            if story:
                story = story.convert_to_story(user)
                session[STORY_KEY] = json.dumps(story.serialize())
            flash(f'Welcome back {user.username}', 'success')
            return redirect('/')

        else: 
            flash('Sign in failed', 'danger')
            return render_template('signin.html', form=form)

    return render_template('signin.html', form=form)



@app.route('/logout')
def logout():
    ''' logs user out & clears flask session '''
    do_logout()
    flash('Logout successful.', 'success')
    return redirect('/')


@app.route('/stories')
def render_stories_index():
    ''' Renders the story index page. A list of all stories. Authentication not needed.'''
    story_list = Story.query.all()

    return render_template('stories_index.html', story_list=story_list)


@app.route('/stories/<story_id>')
def render_story(story_id):

    story = Story.query.get_or_404(story_id)

    return render_template('story_detail.html', story=story)
    

@app.route('/<username>')
def render_user_home(username):

    # if user is logged in as this user, show user home
    if g.user:
        user = User.query.get_or_404(g.user.id)
    
        return render_template('account.html', user=user )
    else:
        return redirect(url_for('render_home'))


#=================== API ROUTES ==================

@app.route('/api/retrieve', methods=['POST'])
def retrieve_story():
    data = request.get_json()
    # print('RETRIEVE REQUEST', data)
    if data == 'none':
        session.pop(STORY_KEY)
        return 'cleared'
    else:
        session[STORY_KEY] = json.dumps(data)
        return 'ok'


@app.route("/api/contribute", methods=["POST"])
def handle_submission():
    """Receive the API call from JS front end. Trigger appropriate functions"""
    # print('NEW CONTRIBUTE REQUEST RECEIVED')

    story = g.story

    text = request.form.get("body")
    content = request.form.get("body")
    story_prompt = request.form.get('story_prompt')
    genre = request.form.get('story_genre')


    if g.user:
        # create a real story if logged in
        if not story:
            story = Story(
                genre = genre,
                story_prompt = story_prompt
                )
        db.session.add(story.contribute(role='user',content=content))
        db.session.add(story)
        db.session.commit()

    else:
        if not story:
            # create a story if one doesn't exist
            story = AnonStory(
                genre = genre,
                story_prompt = story_prompt
                )
        story.contribute(role='user',content=content)
    
    # print('PRINTING story = gstory ',story)
    # print('PRINTING story contributions= gstory ')
    # print([s for s in story.contributions])
    
    # GET AI CONTRIBUTION
    ai_contribution = get_ai_contribution(story)

    
    story.contribute(
        role=ai_contribution["role"],
        content=ai_contribution["content"],
        tokens=ai_contribution["tokens"],
    )

    print('g.user',g.user)
    if session.get(CURRENT_USER_KEY):
        # do this if user is logged in
        # print('logged in submission')
        story.contribute("user", text, user_id=g.user.id)
        db.session.add(story)
        db.session.commit()

    # dump the serialized story into the flask session
    session[STORY_KEY] = json.dumps(story.serialize())


    return jsonify({"role": ai_contribution["role"], "content": ai_contribution["content"]})



@app.route('/api/verify-auth', methods=["GET"])
def verify_auth():
    ''' Check authentication. Returns True if there is a user_id in session '''

    if session.get(CURRENT_USER_KEY):
        return jsonify(is_logged_in = True)
    else:
        return jsonify(is_logged_in = False)


@app.route("/api/restart", methods=["GET"])
def restart():
    clear_story()
    return 'cleared'



#=================== METHODS ==================


def get_recent_contributions(story,num=4):
    ''' Expects an AnonStory or Story object. 
    Returns the most recent num contributions. Defaults to 4. Must have at least one, which should be the user's first contribution'''
    # story = story
    # print('INSIDE get_recent_contributions STORY IS',story)
    # print('INSIDE get_recent_contributions STORY CONTRIBUTIONS ARE',story.contributions)
    return (
        [{role:content for role,content in item.items()} for item in story.contributions[-(min(len(story.contributions), num)):]]
    )

def get_ai_contribution(story):
    ''' Makes an API call to open AI to get the AI's addition to a story. Expects an AnonStory or Story object with a get_recent() method '''

    # get recent additions to the story.    
    recent_conversation = story.get_recent()
    

    if not story.characters:
        character = "Sally"
    else:
        character = story.characters[0]

    system_intro = f"""
    Assume the role of a cooperative author. We're writing a {story.genre} story together. We will take turns adding a sentence or two to the story one sentence at a time. In the example, my name is User and your name is Assistant.
    
    Follow these instructions:
    1. Make your response in fewer than 50 words.
    2. If I write an incomplete sentence, you should finish my sentence.
    3. Make sure the story we write stays on genre.

    Example:
    - User: {character} woke up with a huge headache.
    - Assistant: They knew today would be different.
    - User: {character} looked everywhere, but couldn`t find 
    - Assistant: anything to eat for breakfast. But while looking, suddenly a giant.
    
    This is the most recent section of the story:
    """
    
    system_outtro = f'''

    Add to the story as if you are a cooperative author. Please make sure you follow the rules:
    1. Respond in fewer thn 50 words.
    2. If I write an incomplete sentence, finish my sentence. Otherwise, write full sentences.
    3. This is a {story.genre} story
    '''

    # 3. Always put your response between quotation marks (" ")

    messages = [
        {"role": "system", "content": system_intro},
        {"role": "assistant", "content": story.story_prompt},
        *recent_conversation,
        {"role": "system", "content": system_outtro},
    ]
    print('========= Messages Sent======', messages)

    # make the call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=1, max_tokens=3500
    )

    # Retrieve and clean up the content
    content = response["choices"][0]["message"]["content"]
    total_tokens = response["usage"]["total_tokens"]

    # return the response
    return {
        "role": "assistant",
        "content": content,
        "tokens": total_tokens,
    }
