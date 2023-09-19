window.addEventListener('load',()=>scrollToBottom());

function scrollToBottom() {
    let active_chat_body = document.querySelector('.msg_card_body.active_chat');
    if(active_chat_body){
        // console.log(active_chat_body.cloneNode(true))
        var objDiv = active_chat_body.querySelector(".conversation-body");
        objDiv.scrollTop = objDiv.scrollHeight;
    }
}
function active_chats_remover(){
    // document.getElementById('chat-list-wrapper').classList.toggle('hidden');
    document.getElementById('no-active-chat').classList.toggle('hidden');
    document.getElementById('conv-divs-wrapper').classList.toggle('show-flex');

    let act = document.querySelectorAll('.active_chat');
    act.forEach(chat => {
        chat.classList.remove('active_chat');
    });

    let chat_items = document.querySelectorAll('.chat-item');
    chat_items.forEach(item => {
        item.classList.remove('is_active');
    });
}

function switch_tabs(){
    let chat_list_wrapper = document.getElementById('chat-list-wrapper');
    let conversation_wrapper = document.getElementById('conversation-wrapper');

    if(conversation_wrapper.classList.contains('dorminant-tab')){
        conversation_wrapper.classList.replace('dorminant-tab','hidden-tab');
        chat_list_wrapper.classList.replace('hidden-tab','dorminant-tab');
    }
    else if(chat_list_wrapper.classList.contains('dorminant-tab')){
        chat_list_wrapper.classList.replace('dorminant-tab','hidden-tab');
        conversation_wrapper.classList.replace('hidden-tab','dorminant-tab');
    }
    else{
        chat_list_wrapper.classList.add('dorminant-tab');
        conversation_wrapper.classList.add('hidden-tab');
    }
}

function chat_activation_handler(){
    let chat_items = document.querySelectorAll('.chat-item');
    chat_items.forEach(item => {
        item.addEventListener('click',(e)=>{
            active_chats_remover();
            switch_tabs();
            document.getElementById('no-active-chat').classList.add('hidden');
            document.getElementById('conv-divs-wrapper').classList.add('show-flex');
            item.classList.add('is_active');
            cur_receiverId = item.getAttribute('receiver');
            document.getElementById('chat_body_'+cur_receiverId).classList.add('active_chat');
            scrollToBottom();

            
            let unread_icon=item.querySelector('.unread-icon');
            if(unread_icon){
                let cur_thread = item.id;
                cur_thread = cur_thread.replace('chat_','');
                unread_icon.remove();
                mark_as_read(cur_thread,cur_receiverId)
            }
        })
    });   
}   
chat_activation_handler();

window.addEventListener('keyup',(e)=>{
    if($('#conv-divs-wrapper').hasClass('show-flex')&&$('#no-active-chat').hasClass('hidden')){
        if(e.keyCode === 27){                
            active_chats_remover();
            switch_tabs();
        }                
    }
})    


const USER_ID = $('#logged-in-user').val()      
let loc = window.location;
let wsStart = 'ws://';

if(loc.protocol === 'https') {
    wsStart = 'wss://';
}
let endpoint = wsStart + loc.host + loc.pathname;

var socket = new WebSocket(endpoint);

socket.onopen = async function(e){
    console.log('open', e);
    var msgForm = document.getElementById('msgForm');
    msgForm.addEventListener('submit',submitMessage);
}
socket.onmessage = async function(e){
    console.log('message', e);
    let data = JSON.parse(e.data);
    let message = data['message'];
    let sent_by_id = data['sent_by'];
    let sent_by_name = data['sender_name'];
    let sent_by_photo = data['sender_img'];
    let status = data['status'];
    let thread_id = data['thread_id'];
    newMessage(message, sent_by_id,sent_by_name,sent_by_photo, thread_id,status);
    // socket.close()
}

socket.onerror = async function(e){
    console.log('error', e);
}

socket.onclose = async function(e){
    console.log('close', e);
}
function currentTime(){
    return (new Date().toLocaleTimeString([], { hour: '2-digit', minute: "2-digit", hour12: false}));
}
    

var msgForm = document.getElementById('msgForm');
msgForm.addEventListener('submit',submitMessage);
function submitMessage(e){
    e.preventDefault();
    var msgContent = document.getElementById('msg-input').value;

    
    // let message = input_message.val()
    let send_to = get_receiver_id()
    let thread_id = get_active_thread_id()

    let data = {
        'message': msgContent,
        'sent_by': USER_ID,
        'send_to': send_to,
        'thread_id': thread_id
    }
    data = JSON.stringify(data)
    socket.send(data)
    document.getElementById('msg-input').value=''

}
var inpField = document.getElementById('msg-input');
inpField.addEventListener('keyup',(e)=>{
    if ($("#msg-input:focus") && (e.keyCode === 13)){
        e.preventDefault();
        submitMessage(e)
    }
});

function newMessage(message, sender_id, sender_name, sender_photo, thread_id,status) {
    let send_status;
    if ($.trim(message) === '') {
        return false;
    }
    if(navigator.onLine){
        send_status = status ?'sent' : 'Waiting';
    }
    else{
        send_status = 'waiting';
    }
    // var active_chat_body = document.querySelector('.msg_card_body.active_chat');
    // var messageSection = active_chat_body.getElementById('conversation-body');
    var target_chat_item_id = 'chat_' + thread_id;
    var target_chat_body_id;
    if(sender_id == USER_ID){
        var url_search = window.location.search;
        var chat_item = document.getElementById(target_chat_item_id);
        //check for receiver id from an existing chat-item
        if(chat_item){
            var msgreceiver = chat_item.getAttribute('receiver');
            target_chat_body_id = document.getElementById('chat_body_'+msgreceiver);
            // alert(target_chat_body_id + chat_item+'1'+' '+msgreceiver);
        }
        //when there is no existing chat-item, it's a new chat which comes with a receiver in the URL
        else{
            msgreceiver = url_search.replace('?u=','');
            target_chat_body_id = document.getElementById('chat_body_'+msgreceiver);
            // alert(target_chat_body_id+ target_chat_item_id+'2');
        }
    }
    else{
        //first check if the thread exists
        var chat_item = document.getElementById(target_chat_item_id);
        if(chat_item && document.getElementById('chat_body_'+sender_id)){
            let msgreceiver = chat_item.getAttribute('receiver');
            target_chat_body_id = document.getElementById('chat_body_'+msgreceiver);
            // alert(target_chat_body_id+ target_chat_item_id+'3');
        }
    }
    
    if(sender_id == USER_ID){
        let messageSection = target_chat_body_id.querySelector('.conversation-body');
        var newWrapper = document.createElement('div');
        messageSection.appendChild(newWrapper).classList.add('message-holder','sent-msg');
        var newMsgCont = document.createElement('div');
        
        newWrapper.appendChild(newMsgCont).classList.add('message-body');
        var msgText = document.createElement('p');
        msgText.classList.add('message-text');
        newMsgCont.appendChild(msgText).innerHTML = message;

        let delivery = document.createElement('span');
        delivery.classList.add('delivery-status');
        let delivery_text = document.createElement('small');
        delivery.appendChild(delivery_text).innerHTML = send_status;
        newMsgCont.appendChild(delivery);

        var sendTime = document.createElement('span');
        sendTime.classList.add('message-time');
        newWrapper.appendChild(sendTime).innerHTML = currentTime();
        scrollToBottom();

        let newmsg_thread =document.getElementById('chat_'+thread_id);
        if(newmsg_thread){
            newmsg_thread.querySelector('.latest-text').innerHTML = 'You: '+message;
            let toreplace = newmsg_thread.cloneNode(true)
            document.getElementById('chat-list').insertAdjacentElement("afterbegin",toreplace)
            newmsg_thread.remove()
            chat_activation_handler();
        }
        else{
            let receiver_name = target_chat_body_id.querySelector('.conversation-header').querySelector('.receiver_name').innerHTML;
            let receiver_photo = target_chat_body_id.querySelector('.conversation-header').querySelector('img').src;
            let chat_item_template = `
            <div class="chat-item is_active" id="chat_${thread_id}" receiver="${msgreceiver}">
                <img src="${receiver_photo}" alt="user">
                <div class="text-preview">
                    <span class="thread_user_name">${receiver_name}</span>
                    <p class='latest-text'>You: ${message}</p>
                </div>
            </div>`;
            document.getElementById('chat-list').insertAdjacentHTML("afterbegin",chat_item_template);
            if(document.getElementById('chat-list').querySelector('.empty-container')){
                document.getElementById('chat-list').querySelector('.empty-container').classList.add('hidden');
            }                
            chat_activation_handler();
        }

    }
    else{
        // let newmsg_thread =document.getElementById('chat_'+thread_id);
        if(chat_item){
            let messageSection = target_chat_body_id.querySelector('.conversation-body');
            var newWrapper = document.createElement('div');
            messageSection.appendChild(newWrapper).classList.add('message-holder','received-msg');
            var newMsgCont = document.createElement('div');
            
            newWrapper.appendChild(newMsgCont).classList.add('message-body');
            var msgText = document.createElement('p');
            msgText.classList.add('message-text');
            newMsgCont.appendChild(msgText).innerHTML = message;

            var sendTime = document.createElement('span');
            sendTime.classList.add('message-time');
            newWrapper.appendChild(sendTime).innerHTML = currentTime();
            scrollToBottom();

            let newmsg_thread =document.getElementById('chat_'+thread_id);
            if(newmsg_thread){
                newmsg_thread.querySelector('.latest-text').innerHTML = message;
                let toreplace = newmsg_thread.cloneNode(true)
                toreplace.insertAdjacentHTML("beforeend",'<i class="unread-icon bi-record-fill green-el"></i>');
                document.getElementById('chat-list').insertAdjacentElement("afterbegin",toreplace)
                newmsg_thread.remove();
            }
            chat_activation_handler();
        }
        else{
            let chat_body_template = `                    
                <div class="msg_card_body" id="chat_body_${sender_id}">
                    <div class="conversation-header">
                        <div class="receiver-data">
                            <img src="/static${sender_photo}" alt="user">
                            <span>${sender_name}</span>
                        </div>
                        <p>1 messages</p>
                        <span class="actions-btn bi-three-dots-vertical"></span>
                    </div>
                    <div class="conversation-body y-scrollable" id="conversation-body">
                        <div class="message-holder received-msg">
                            <div class="message-body">
                                <p class="message-text">${message}</p>
                            </div>                
                            <span class="message-time">${currentTime()}</span>
                        </div>
                    </div>
                </div>`;
            document.getElementById('conv-divs-wrapper').insertAdjacentHTML("afterbegin",chat_body_template);

            let chat_item_template = `
            <div class="chat-item" id="chat_${thread_id}" receiver="${sender_id}">
                <img src="/static${sender_photo}" alt="user">
                <div class="text-preview">
                    <span class="thread_user_name">${sender_name}</span>
                    <p class='latest-text'>${message}</p>
                </div>
                <i class="unread-icon bi-record-fill green-el"></i>
            </div>`;
            document.getElementById('chat-list').insertAdjacentHTML("afterbegin",chat_item_template);
            if(document.getElementById('chat-list').querySelector('.empty-container')){
                document.getElementById('chat-list').querySelector('.empty-container').classList.add('hidden');
            }
            chat_activation_handler();
        }
    }
}       
    


function get_receiver_id(){
    let receiver_id_field = document.querySelectorAll('.msg_card_body.active_chat')[0];
    let receiverId;
    if (receiver_id_field){
        let receiver = receiver_id_field.id;
        receiverId = receiver.replace('chat_body_', '');
    }
    else{
        console.log('receiver not found');
        receiverId = '';
    }
    return receiverId;
}

function get_active_thread_id(){
    let chat_id_field = document.querySelectorAll('.chat-item.is_active')[0];
    let thread_id;
    if (chat_id_field){
        chat_id = chat_id_field.id;
        thread_id = chat_id.replace('chat_', '');
    }
    else{
        console.log('new thread');
        thread_id = 'create_new';
    }
    return thread_id;
}
function search_chat_list() {
    var input, filter, chat_list, chat_items, td, txtValue;
    input = document.getElementById("id_chat_search");
    filter = input.value.toUpperCase();
    chat_list = document.getElementById("chat-list");
    chat_items = chat_list.querySelectorAll(".chat-item");
    chat_items.forEach(chat_item => {    
        chat_item.style.display = "none";
        td = chat_item.querySelectorAll('.thread_user_name');
        for (var j = 0; j < td.length; j++) {
            cell = chat_item.querySelector('.thread_user_name');
            if (cell) {
                txtValue = td[j].innerHTML;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    chat_item.style.display = "";
                    break;
                } 
                else {
                    chat_item.style.display = "none";
                }
            }
        }

    });
}


function mark_as_read(thread_id,sender_id){    
    const USER_ID = $('#logged-in-user').val()      
    let loc = window.location;
    let wsStart = 'ws://';

    if(loc.protocol === 'https') {
        wsStart = 'wss://';
    }
    let endpoint = wsStart + loc.host + '/chat-seen/';

    var socket = new WebSocket(endpoint);

    socket.onopen = async function(e){
        console.log('open', e);
        let data = {
            'chat_thread': thread_id,
            'chat_sender': sender_id,
            'chat_receiver': USER_ID,
        }
        data = JSON.stringify(data)
        socket.send(data)
    }
    socket.onmessage = async function(e){
        console.log('message', e);
        let data = JSON.parse(e.data);
        let feedback = data['feedback'];
        let status = data['status'];
        socket.close()
    }

    socket.onerror = async function(e){
        console.log('error', e);
    }

    socket.onclose = async function(e){
        console.log('close', e);
    }  
    
}

var close_chat_btns = document.querySelectorAll('.close-chat');
close_chat_btns.forEach(btn => {
    btn.addEventListener('click',()=>{
        active_chats_remover();
        switch_tabs();
        btn.parentElement.classList.remove('show-flex');
    });
});

var hide_chat_arrows = document.querySelectorAll('.hide_chat_arrow');
hide_chat_arrows.forEach(arrow => {
    arrow.addEventListener('click',()=>{
        active_chats_remover();
        switch_tabs();
    });
});

function heightFitter(ele){
    var ele = document.getElementById(ele);
    ele.style.height = 'auto'; ele.style.height = ele.scrollHeight + 'px';
}

$('#msg-input').emojioneArea(
    {pickerPosition:"top"}
);


var emojisLinkBtn = document.getElementById('emoji-btn');
var input =  document.getElementById('msg-input');
emojisLinkBtn.addEventListener('click',showEmojis);
function showEmojis(){
    document.getElementById('emojisWrapper').classList.toggle('show-flex');
    document.getElementById('msg-input').focus();
    // loadEmoji();
}
function copyEmoji(k) {
    let cursorPos = input.selectionStart;
    input.focus();
    let v = input.value;
    let textBefore = v.substring(0, cursorPos);
    let textAfter = v.substring(cursorPos, v.length);
    input.value = textBefore + k + textAfter;
    cursorPos += k.length;
    input.focus();
    input.setSelectionRange(cursorPos, cursorPos);

}
let onlineStatus = `Your network status is ${navigator.onLine?"Online":"Offline"}`;
console.log(onlineStatus)
const emojisList= document.getElementById('emojisList');
const emojiSearch= document.getElementById('emojiSearch');
if(navigator.onLine){
    fetch('https://emoji-api.com/emojis?access_key=14e2c7e03284fd7604d6f1cd1bf5426d523d736d')
    .then(res=>res.json())
    .then(data=>loadEmoji(data))
}


function loadEmoji(data){
    data.forEach(emoji=>{
        let li = document.createElement('span');
        li.setAttribute('emoji-name',emoji.slug);
        li.setAttribute('onclick','copyEmoji(\''.concat(emoji.character).concat('\')'));
        li.classList.add('emojiChar');
        li.textContent=emoji.character;
        emojisList.appendChild(li);
    })
}
emojiSearch.addEventListener('keyup',e=>{
    let value = e.target.value;
    let emojis=document.querySelectorAll('#emojisList span');
    emojis.forEach(emoji=>{
        if(emoji.getAttribute('emoji-name').toLocaleLowerCase().includes(value)){
            emoji.style.display = 'flex';
        }
        else{
            emoji.style.display = 'none';
        }
    })
})