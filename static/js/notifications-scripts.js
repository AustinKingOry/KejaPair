let cards = document.querySelectorAll('.notif-card,.unread-item');
cards.forEach(card=>{
    card.onclick=(e)=>{
        let id=card.getAttribute('notif-id');
        clear_notification(id);
    }    
});
function clear_notification(id){
    let notification_id = id;
    if((notification_id).toLowerCase()=='clear_all_btn'){
        let status=request_cl('*','clear');
        if(status){
            window.location.reload(true); 
        }
        else{
            window.location.reload(true); 
        }                          
    }
    else{
        let status=request_cl(notification_id,'clear');
        let notif_url = document.getElementById('notif'+id).getAttribute('href');
        location.href=notif_url;
        console.log(notif_url)
    }
}
function request_cl(notif_id,request_type){
    let status=false
    let wsStart = 'ws://';
    if(window.location.protocol == 'https'){
        wsStart = 'wss://';
    }
    let socket_url = wsStart + window.location.host + '/clear-notification/';
    let socket  = new WebSocket(socket_url);

    socket.onopen = async function(e){
        console.log('open',e);
        let data = {
            'notif_id':notif_id,
            'rqst_type':request_type,
            'request_user':document.getElementById('USER_ID').value,
        }
        data = JSON.stringify(data);
        socket.send(data);
    }
    socket.onmessage = async function(e){
        console.log('message',e);
        let data = JSON.parse(e.data);
        let feedback = data['feedback'];
        let status = data['status'];
        let txt_feedback = feedback;
        // make_toast(txt_feedback,status);
        socket.close();
        return status;
    }
    socket.onclose = async function(e){
        console.log('close',e);
    }
    socket.onerror = async function(e){
        console.log('error',e);
    }

    return status;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

document.getElementById('notif-categories').addEventListener('change',filter_notifications)
function filter_notifications(){
    let value = document.getElementById('notif-categories').value;
    console.log(value)
    let notif_cards = document.querySelectorAll('.notif-card');
    notif_cards.forEach(card=>{
        let category = card.getAttribute('cat');
        if(value!='*'){
            if(value.toLowerCase()!=category.toLowerCase()){
                card.style.display = 'none';
            }
            else if(value.toLowerCase()===category.toLowerCase()){
                card.style.display = null;
            }
        }
        else{
            card.style.display = null;
        }
    });
}
    