let story = {'context':{},'contributions':[]}
const storyDiv = $('#story')

const contributionSection = $('#contribuionSection')
const inputForm = $('#inputForm')
let contextDiv = $('#contextDiv')
let newStoryBtn = $('#newStoryBtn')
let logoutLink = $('.logoutLink')

const signUpModal = $('#signUpModal')
const signInModal = $('#authModal')



function randomizePrompt(e){
    
    // e.preventDefault()
    // randomize the genre
    let genreOptions = $('#genre option');

    let randomIndex = Math.floor(Math.random() * genreOptions.length);
    $('#genre').prop("selectedIndex", randomIndex)

    // randomize the prompt
    prompts = 
        [
        'There was never enough time.',
        'I used to wonder what happened to Roger.',
        'One day I woke up to discover I had more arms than usual.',
        'Everyone accepted him as King, but only she knew the truth.',
        "We were 3 best friends for 20 years, until yesterday.",
        "We met in the most trivial of places.",
        'I used to think "til death do us part" was just a thing you said.',
        'I get coffee the same way every morning. But today was different.',
        "It didn't matter how hard I tried.",
        "It didn't matter how hard she tried.",
        "Business was booming but it never lasts.",
        '"See, I told you it would work," I said.'

    ]
    let promptIndex = Math.floor(Math.random()* prompts.length)
    $('#storyPrompt').val(prompts[promptIndex]);
}

$('#randomizePrompt').click(randomizePrompt)
$(document).ready(randomizePrompt)

//  Handle submission of context form
function processContextForm(e) {
    // Handling of this form is client-side only.
    e.preventDefault();
    // console.log('story started')
    let contextGenre = $('#genre')
    let contextPrompt = $('#storyPrompt')
    // populate the story form with these values
    let storyGenre = $('#story_genre')
    let storyPrompt = $('#story_prompt')
    
    storyGenre.val(contextGenre.val())
    storyPrompt.val(contextPrompt.val())
    
    $('#storyGenreHeadline').text(contextGenre.val())
    $('#storyPromptHeadline').text(contextPrompt.val())
    $('.context-form').addClass('d-none')
    $('.context-form').removeClass('d-block')
    $('.contribution-form').removeClass('d-none')
    $('.contribution-form').addClass('d-block')


    // update story variable. Do I need to do this?
    story.context= {
        'genre':$('#genre').val(),
        'story_prompt':$('#storyPrompt').val()
    } 
}


// handle submission of Story form
async function processStoryForm(e) {
    e.preventDefault();

    formData = new FormData(this);
    // console.log(this) // evaluates to the form element
    
    let userText = this.elements['inputField'].value
    updateStoryDiv(userText, 'user');
    
    // Send the user's contribution to the server. Expect assistant contribution in response.
    let response = await serverRequest(formData);
    
    updateStoryDiv(response.content, response.role)
    
    // update the story variable and store it
    story.contributions.push({'role':'user','content':userText})
    story.contributions.push({'role':response.role,'content':response.content})
    storeStory();

    $('#inputField').val('') //clear out the field
}


//send the user's input to server
async function serverRequest(formData){
    
    // console.log('request sent:', JSON.stringify(formData.entries()))
    // console.log('values', formData.values())
    
    let response = await $.ajax({
        type: 'POST',
        url: `/api/contribute`,
        data: formData,
        processData: false,
        // contentType: 'application/json',
        contentType: false,
        success: function() {
            // updateStoryDiv(result,'ai')
            // addListeners()
            
        },
        error: function(){
            alert('Oh no! Something went wrong.')
        }
    })
    return response
}


async function processSignIn(e){
    // console.log('processSignIn called')

    e.preventDefault();

    formData = new FormData(this);

    let response = await $.ajax({
        type: 'POST',
        url: `/signin`,
        data: formData,
        processData: false,
        // contentType: 'application/json',
        contentType: false,
        success: function(response) {
            // updateStoryDiv(result,'ai')
            // console.log(response)
            signInModal.modal('hide')
            
        },
        error: function(){
            alert('Oh no! Something went wrong.')
        }
    })
    // return response
    // Set the user variable

}


function storeStory(){
    //store in storage
    localStorage.setItem('story',JSON.stringify(story))
}

function passStory(){
    //pass story to server
    let savedStory = localStorage.getItem('story',JSON.stringify(story))

    // console.log('saved story', savedStory)

    if (savedStory) {
        // console.log('savedstory true')
        $.ajax({
            url:'/api/retrieve',
            type: 'POST',
            data: savedStory,
            contentType: 'application/json'
        })
    }
    else {
        // console.log('savedstory false')
        $.ajax({
            url:'/api/retrieve',
            type: 'POST',
            data: JSON.stringify('none'),
            contentType: 'application/json'
        })
    }
    
}

function clearStory(){
    // clear the story from local storage
    localStorage.removeItem('story');    
    let response = $.get('/api/restart',function(){
        location.href = '/'
        location.reload()
    })
}



//Render the returned text on page
function updateStoryDiv(content,role){
    // console.log('text is',content)
    let span = $('<span />').attr('class',role).html(' '+content);

    storyDiv.append(span)
}






// Add event listeners to forms

function addListeners(){
    
    inputForm.submit(processStoryForm)

    let contextForm = $('#contextForm')
    contextForm.submit(processContextForm)

    logoutLink.click(clearStory)

    newStoryBtn = $('#newStoryBtn')
    newStoryBtn.on('click',clearStory)
}

addListeners();

// pass current local storage to app
passStory();
