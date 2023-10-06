import openai
import os
from models import db, connect_db, User, Story, Contribution, Guest, AnonStory

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_contribution(story):
    ''' '''
    
    # story = db.session.get(Story,session['story']['id'])

    # construct the prompt
    # recent_conversation = get_recent_contributions(story)
    recent_conversation = story.get_recent()
    print('recent conversation in get_ai_contribution',recent_conversation)
    

    if not story.characters:
        character = "Sally"
    else:
        character = story.characters[0]

    system_instructions = f"""
    Assume the role of a cooperative author. We`'re writing a {story.genre} story together. We are taking turns adding to the story one sentence at a time. Your name is Assistant. My name is User.
    
    Follow these instructions:
    1. Make your response in fewer than 50 words.
    2. If I write an incomplete sentence, you should finish my sentence. Then start another incomplete sentence.

    Example:
    - User: {character} woke up with a huge headache.
    - Assistant: They knew today would be different.~
    - User: {character} looked everywhere, but couldn`t find
    - Assistant: anything to eat for breakfast. But while looking, suddenly a giant

    """
    # 3. Always put your response between quotation marks (" ")

    messages = [
        {"role": "system", "content": system_instructions},
        {"role": "assistant", "content": story.story_prompt},
        *recent_conversation,
        {"role": "system", "content": system_instructions},
    ]
    print('=========messages sent======', messages)

    # make the call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=1, max_tokens=3500
    )

    # Retrieve and clean up the content
    content = response["choices"][0]["message"]["content"]
    total_tokens = response["usage"]["total_tokens"]
    # add the contribution to the story
    """ def add_to_story(self,role,text,guest_id=None,user_id=None): """

    print(
        {
            "role": "assistant",
            "content": content,
            "tokens": total_tokens,
        }
    )

    # return the response
    return {
        "role": "assistant",
        "content": content,
        "tokens": total_tokens,
    }
