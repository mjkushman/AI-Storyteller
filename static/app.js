
let STORY
const submitButton = $('#submit')
const contributionSection = $('#contribuionSection')
let inputForm
let contextDiv = $('#contextDiv')



function randomize_prompt(e){
    // console.log('randomize_prompt called. e:',e)
    e.preventDefault()
    let genre = $('#genre').val()
    console.log(genre)
    prompts = 
        [
        'There was never enough time for',
        'I used to wonder what happened to Roger. But now,',
        'One day I woke up to discover I had more arms than usual.',
        'They called him "King", but only I knew the truth.',
        'We were 3 best friends. And until yesterday I didn\'t think anything could change that.',
        'We met in the most trivial of places.',
        'I get coffee at the same place every morning and I know the staff well. But today there was someone knew behind the counter. I read her name tag.',
        'No matter how hard I try,',
        'No matter how hard she tried,',
        'Business was booming, but',
        '"See, I told you it would work," I said to my friend.'

    ]

    let promptIndex = Math.floor(Math.random()* prompts.length)
    $('#storyPrompt').val(prompts[promptIndex]);
}

$('#randomizePrompt').click(randomize_prompt)


//  Handle submission of context form
async function processContextForm(e) {
    e.preventDefault();
    console.log('story started')
    let context = $(this).serialize()
    
    // send the start request to server, receive story id
    await startRequest(context)    
    // console.log('awaited response',response)
}


// Send a request to start a new story to the server. Requires the context of the story, like genre.
function startRequest(context){
    let response = $.ajax({
        type: 'GET',
        url: `/api/new?${context}`,
        success: function(data){
            // console.log('this is the data',data)
            contributionSection.html(data) // render the new form on page
            addListeners();
            $(contextDiv).remove(); //remove the context form
            STORY = $('#story') // set story section variable
        },
        error: function(){
            alert('something went wrong')
        }
    })
}




// handle submission of Story form
async function processStoryForm(e) {
    e.preventDefault();

    // let contribution = $('#inputField').val()
    // let contributionSerial = $(this).serialize()

    formData = new FormData(this);
    
    console.log('this',this)
    // console.log('this values',this.elements['inputField'].value)
    // console.log('formData',formData);

    let userText = this.elements['inputField'].value
    updateStory(userText, 'user');

    // Send the user's contribution to the server. Expect assistant contribution in response.
    let response = await serverRequest(formData);
    // console.log('CONTRIBUTION FIELD',$('#inputField'))
    $('#inputField').val('') //clear out the field

    updateStory(response.body, response.role)
}


//send the user's input to server
async function serverRequest(formData){
    
    console.log('request sent:', JSON.stringify(formData.entries()))
    console.log('values', formData.values())

    let response = $.ajax({
        type: 'POST',
        url: `/api/contribute`,
        data: formData,
        processData: false,
        // contentType: 'application/json',
        contentType: false,
        success: function() {
            // updateStory(result,'ai')
            
        },
        error: function(){
            alert('Oh no! Something went wrong.')
        }
    })
    return response
    // console.log('contribution response',response)

    // let response = await axios.get(`/api/contribute?contribution=${contribution}`)
    // console.log(response)
    // let ai_text = response.data.ai_story
    // updateStory(ai_text,'ai')
}







//Render the returned text on page
function updateStory(body,role){
    // console.log('updateStory called on',body,role)
    console.log('text is',body)
    let span = $('<span />').attr('class',role).html(' '+body);

    STORY.append(span)
}






// Add/update event listeners to forms

function addListeners(){
    inputForm = $('#inputForm')
    inputForm.submit(processStoryForm)

    let contextForm = $('#contextForm')
    contextForm.submit(processContextForm)
}

addListeners();