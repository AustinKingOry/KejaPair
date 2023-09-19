function set_hobby_from_list(){
    var all_hobby_options = document.querySelectorAll('.hobby-option');
    var user_hobby_list = document.getElementById('hobbies-list');
    all_hobby_options.forEach(hobby_opt => {
        hobby_opt.addEventListener('click',(e)=>{
            let text = hobby_opt.querySelector('span').innerHTML;
            if(!hobby_opt.classList.contains('is_listed')){
                new_hobby(text)
            }
            hobby_opt.classList.add('is_listed')
            hobby_opt.querySelector('i').classList.replace('bi-plus','bi-check')
        });
    });
}
set_hobby_from_list();

document.getElementById('new_from_search').onclick=(e)=>{
    create_from_search();
    search_hobbies();
}
function create_from_search(){
    let text = document.getElementById("id-hobby-search-input").value;
    new_hobby(text);
    document.getElementById("id-hobby-search-input").value='';
    document.getElementById('new_from_search').style.display='none';
    let opt_template = `
    <div class="hobby-option is_listed">
        <span>${text}</span>
        <i class="bi-check bold add-hobby"></i>
    </div>`;
    document.getElementById('hobby-options').insertAdjacentHTML('afterbegin',opt_template);
    set_hobby_from_list();
}

const new_hobby = (text) =>{
    var user_hobby_list = document.getElementById('hobbies-list');

    if(user_hobby_list.querySelectorAll('.hobby-item').length==0){
        user_hobby_list.innerHTML = "";
    }
    let user_hobby_template = `<div class="hobby-item"><p>${text}</p><span class="bi-x remove-hobby"></span></div>`;
    user_hobby_list.insertAdjacentHTML('beforeend',user_hobby_template);
    remove_option();
}

function search_hobbies() {
    var input, filter, hobby_opt_list, hobby_option_items, td, txtValue;
    input = document.getElementById("id-hobby-search-input");
    filter = input.value.toUpperCase();
    hobby_opt_list = document.getElementById("hobby-options");
    hobby_option_items = hobby_opt_list.querySelectorAll(".hobby-option");
    hobby_option_items.forEach(hobby_option => {    
        hobby_option.style.display = "none";
        td = hobby_option.querySelectorAll('span');
        for (var j = 0; j < td.length; j++) {
            cell = hobby_option.querySelector('span');
            if (cell) {
                txtValue = td[j].innerHTML;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    hobby_option.style.display = "";
                    hobby_option.classList.add("search-result");
                    break;
                } 
                else {
                    hobby_option.style.display = "none";
                    hobby_option.classList.remove("search-result");
                }
            }
        }
        if(document.querySelectorAll('.search-result').length==0){
            document.getElementById('new_from_search').style.display='flex';
        }
        else{
            document.getElementById('new_from_search').style.display='none';
        }

    });
    if(hobby_option_items.length==0){
        if(input.value!=''){
            document.getElementById('new_from_search').style.display='flex';
        }
        else{            
            document.getElementById('new_from_search').style.display='none';
        }
    }
}

// restrict double entry 

var sendHobbies = document.getElementById("sendHobbies");
if(sendHobbies){
    sendHobbies.onclick=(e)=>{
        let request_user = document.getElementById('USER_ID').value;
        let hobby_list_wrapper = document.getElementById('hobbies-list').querySelectorAll('.hobby-item');
        let hobby_list = new Array;
        hobby_list_wrapper.forEach(item => {
            hobby_list.push(item.querySelector('p').innerHTML);
        });
        console.log(hobby_list)


        let wsStart = 'ws://';
        if(window.location.protocol == 'https'){
            wsStart = 'wss://';
        }
        let socket_url = wsStart + window.location.host + '/hobbies-handler/';
        let socket  = new WebSocket(socket_url);

        socket.onopen = async function(e){
            console.log('open',e);
            let data = {
                'hobby_list':hobby_list,
                'request_user':request_user,
            }
            data = JSON.stringify(data);
            socket.send(data);
        }
        socket.onmessage = async function(e){
            console.log('message',e);
            let data = JSON.parse(e.data);
            let feedback = data['feedback'];
            let status = data['status'];
            let hobbies = data['hobbies'];
            let txt_feedback = feedback;
            make_toast(txt_feedback,status);

            if(status){
                sendHobbies.classList.add('bi-check-circle-fill');
                sendHobbies.innerHTML = ' Updated';
            }
            else{
                sendHobbies.classList.add('bi-exclamation-triangle-fill');
                sendHobbies.innerHTML = ' Failed';
            }

            socket.close();
        }
        socket.onclose = async function(e){
            console.log('close',e);
        }
        socket.onerror = async function(e){
            console.log('error',e);
        }
    }
}

function remove_option(){
    var remove_hobby_btns = document.querySelectorAll('.remove-hobby');
    remove_hobby_btns.forEach(btn => {
        btn.onclick=(e)=>{
            let text = btn.previousElementSibling.innerHTML;
            let opt_template = `
            <div class="hobby-option">
                <span>${text}</span>
                <i class="bi-plus bold add-hobby"></i>
            </div>`;
            let status=reset_option(text);
            if(!status){
                document.getElementById('hobby-options').insertAdjacentHTML('afterbegin',opt_template);
            }
            btn.parentElement.remove();
        }
    });
}
remove_option();

function reset_option(text){
    let options = document.querySelectorAll('.hobby-option');
    let status=false;
    options.forEach(option=>{
        if(text == option.querySelector('span').innerHTML){
            option.classList.remove('is_listed');
            option.querySelector('i').classList.replace('bi-check','bi-plus')
            status=true;
        }
    });
    return status;
}

function match_hobbies(){
    let options = document.querySelectorAll('.hobby-option');
    let existing_items = document.querySelectorAll('.hobby-item');

    options.forEach(option=>{
        existing_items.forEach(item => {
            if(item.querySelector('p').innerHTML == option.querySelector('span').innerHTML){
                option.classList.add('is_listed');
                option.querySelector('i').classList.replace('bi-plus','bi-check')
            }
        });
    })
}
match_hobbies();

