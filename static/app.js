const STORY = document.getElementById('story')
let userInput = document.getElementById('userInput')
const submitButton = document.getElementById('submit')


//handle button click
// submitButton.addEventListener('click',function(e){
//     console.log('button click event')
//     e.preventDefault();
//     //run code on userInput;
//     addToStory(userInput.value,'user');
//     sendUserInput(userInput.value);
//     userInput.value = '' //clear out the field
// })


//send the user's input to server
// async function sendUserInput(userInput){
//     console.log('request sent:',userInput)
//     response = await axios.get(`http://127.0.0.1:5000/send-story/${userInput}`)
//     console.log(response)
//     let ai_text = response.data.ai_story
//     addToStory(ai_text,'ai')
// }



//Render the returned text on page
function addToStory(text,contributor){
    console.log('text is',text)
    let span = document.createElement('span')
    span.classList.add(contributor)
    span.insertAdjacentText('beforeend'," ")
    span.insertAdjacentText('beforeend',text)
    // for (char of text) {
    //     span.insertAdjacentText('beforeend', char)
    //     // span.innerText += letter
    // }
    STORY.appendChild(span)
}