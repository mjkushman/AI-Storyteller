# Write Along

Write Along lets you co-write a creative short story with help from an AI assistant.

Take turns adding to a story and be surprised at your creativity.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Contributing](#contributing)

## Overview

Write Along is built using Python and Flask web framework with PostgreSQL database.
When an unauthenticated user creates a new story, an anonymous story object is instantiated. The anonymous story is saved to local storage to persist if the user leaves site or navigates around.

![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/c777a57e-7063-40eb-b984-e3823e6e5fb5)


### Contributing to a story
On  `/`, a user may contribute to a story, a sentence or two at a time. After each contribution, the AI will make its own contribution. This process continues as long as the user wants.

When a user submits their contribution, an API request is made to OpenAI which includes important story context and instructions. OpenAI's LLM will respond with the next sentence in the story.
![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/b38d4fa3-db83-4a13-a986-03488821da60)

![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/4c5dd441-b5e5-4f65-ac63-0a61d056c981)


## Features

- **Create a new Story**
  *   User selects a genre from a list and chooses a starting prompt.
  *   Genre and Prompt are randomly filled, however the Prompt may be cleared and the user may write their own from scratch.
  *   By default for unauthorized users, an `AnonStory` class object is instanced. If the user is authenticated, a `Story` class object is instanced.
    * If a user is currently contributing to an `AnonStory` and then authenticates, the `convert_to_story` method converts the `AnonStory` to `Story`. The new `Story` gets committed to the database and is used for further contribution. `AnonStory` objects are not committed to the databse.
- **Contribute to a Story**
  * The user can start or continue writing the story based on the genre anad prompt. Genre and Prompt are saved as context in the `AnonStory` and `Story` objects.
  * When a user submits their contribution, an API request is made to OpenAI which includes important story context and instructions. OpenAI's LLM will respond with the next sentence in the story.
   The LLM is given `story.genre`, `story.prompt`, `recent_conversation`, plus the following instructions. However it sometimes ignores the word limit:

    ``` 
    Make your response in fewer than 50 words.
    If I write an incomplete sentence, you should finish my sentence.
    Make sure the story we write stays on genre.

  * The full prompt is available in `app.py` 


- **Skip your turn**
  * A user can pass their turn entirely, which prompts the AI to go again.
- **Authentication and Story saving**
  * A user may create an account. Creating an account allows the user to save end edit their story. 
  * If authenticated, a user's story is automatically saved after each Contribution
  * ![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/fcb945e5-222a-474b-96fa-97608968560c)

- **Stories page**
  * `/stories` lists all saved stories. An authenticated user will see an option to edit stories they have created.
  * ![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/90cdd797-8a96-4e63-ab89-d6fbd86f504d)
  * ![image](https://github.com/mjkushman/AI-Storyteller/assets/31631046/5479ba63-8ee5-4023-bab4-c0de9d09f012)


- **Contact me**
  * Simple web form uses `flask_mail` to send an email to contact@writealong.xyz.




## Getting Started

This project uses Python, Flask, and OpenAI to generate captivating stories. Whether you're a developer interested in exploring AI-powered storytelling or a user looking for creative narratives, this project has something for you.


## Installation

Follow these steps to get AI-Storyteller up and running on your local machine:

1. Clone the repository:

   ```bash
   git clone https://github.com/mjkushman/AI-Storyteller.git

2. Create your own OpenAI API key and save it as an environment variable "OPEN_API_KEY"


## Contributing

Yes, I know it's a mess. But it's a mostly functional mess.

I welcome ideas and improvements.


### Entity Relationships
View the diagram in this lucid chart:
https://lucid.app/lucidchart/33463c9f-f715-439e-940b-d0a4991cbf30/edit?viewport_loc=-1147%2C-470%2C2634%2C1530%2C0_0&invitationId=inv_a1d6cb9d-2ec0-4c4b-9bee-526d2ebcfa7f
