var cooldownOver = true;
var index = 0;
var delay = 100; // typing speed in milliseconds
var lineDelay = 500; // delay before starting a new line
var index2 = 0;
var promptValue = "";
var chatID = 0;
var answerText = '';
var isListening = false;
const container = document.querySelector('#chat-container-id');

function typeText(text) {
    const htmlElement = this.addChatElement();
    if (this.index < text.length) {
      if (text.charAt(this.index) === '\n') {
        htmlElement.innerHTML += '\n';
        this.index++;
        setTimeout(() => this.typeText(text), this.lineDelay);
      } else {
        htmlElement.innerHTML += text.charAt(this.index);
        this.index++;
        setTimeout(() => this.typeText(text), this.delay);
      }
    }
    else {
      this.chatID++;
      this.index = 0;
    }
  }
  function handleClick(prompt, event) {
    if(event.code == "Enter"){
    console.log(event);
        if(this.cooldownOver){
            prompt = this.addLineBreaks(prompt, 35);
            prompt = "User: " + prompt;
            this.typeText(prompt);
            const answer = "Pflanze: " + "Mir geht es gut.";
            this.cooldownOver = false;
            setTimeout(() => {
              this.typeText(answer);
            }, 3000);
            setTimeout(() => {
              this.cooldownOver = true;
            }, 8000);
        }
    }
  }
  function addChatElement() {
    const parent = document.querySelector('#chat-container-id');
    if(this.chatID >= parent.children.length){
      const chatElement = document.createElement('div');
      parent.appendChild(chatElement);
      chatElement.classList.add('chat-item');
      return chatElement;
    }
    else {
      const element = parent.children[this.chatID];
      return element;
    }
  }
  function addLineBreaks(str, x) {
    let result = '';
    for (let i = 0; i < str.length; i += x) {
      result += str.substr(i, x) + '\n';
    }
    return result;
  }
// document.addEventListener("DOMContentLoaded", () => {
//     document.getElementById("prompt").addEventListener("keydown", (event) => {
//         handleClick(event.srcElement, event);
//     });
// });