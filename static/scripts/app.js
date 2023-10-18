let story = localStorage.getItem('story')
if (story == null) {
    story = {context:{},contributions:[]}
}

const storyDiv = $('#story')


const contributionSection = $('#contribuionSection')
const inputForm = $('#inputForm')


let contextDiv = $('#contextDiv')
let newStoryBtn = $('#newStoryBtn')
let logoutLink = $('.logoutLink')

const signUpModal = $('#signUpModal')
const signInModal = $('#authModal')
const skipTurn = $('.skip-turn')


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



// handle submission of Story form
async function processStoryForm(e) {
    e.preventDefault();
    formData = new FormData(this);
    // console.log(this) // evaluates to the form element
    // Add user's text to story.
    let userText = this.elements['inputField'].value
    updateStoryDiv(userText, 'user');
    
    // Send the user's contribution to the server. Expect assistant contribution in response.
    let response = await $.ajax({
        type: 'POST',
        url: `/api/contribute`,
        data: formData,
        processData: false,
        // contentType: 'application/json',
        contentType: false,
        success: function(data) {
            // Update the story div upon success
            updateStoryDiv(data.latest.content, data.latest.role)
            // update the story variable and store it
            story = data.story
            storeStory();
        },
        error: function(){
            alert("Oh no! Trouble reaching the server.")
        }
    })

    $('#inputField').val('') //clear out the field
}


function storeStory(){
    //store in storage
    
    localStorage.setItem('story',JSON.stringify(story))
    // localStorage.setItem('story',story)
}

function passStory(){
    //pass story to server
    let savedStory = localStorage.getItem('story')

    // console.log('saved story', savedStory)
    if (!savedStory){
        savedStory = JSON.stringify('');
    }
    
    $.ajax({
        url:'/api/retrieve',
        type: 'POST',
        data: savedStory,
        contentType: 'application/json',
        success: function(data) {
            story = data.story;
            storeStory()},
        error: function(){
            alert('Something went wrong exchanging story with server')}
    })
}

function clearStory(){
    // clear the story from local storage
    localStorage.removeItem('story');    
    let response = $.get('/api/restart',function(){
        location.href = '/'
        // unnnecessary reload?
        // location.reload()
    })
}


//Render the returned text on page
function updateStoryDiv(content,role){
    // console.log('text is',content)
    let span = $('<span />').attr('class',role).html(' '+content);
    // storyDiv.append(span)
    span.insertBefore($('#typing-message'))
    if(role=='user'){
        $('.typing-message').show()
        $('#turn-notice').hide()
    }
    else {
        $('.typing-message').hide()
        $('#turn-notice').show()
    }
}


// Add event listeners to forms
inputForm.submit(processStoryForm)

function addListeners(){

    logoutLink.click(clearStory)

    newStoryBtn = $('#newStoryBtn')
    newStoryBtn.on('click',clearStory)
}

addListeners();

// pass current local storage to app
passStory();
