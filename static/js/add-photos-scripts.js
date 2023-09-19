var new_photo_btn = document.getElementById('new-photo-btn');
var pre_submit_edit_container = document.getElementById('pre-submit-edit-container');
var photo_form = document.getElementById('photo-form');
var finalize_edit = document.getElementById('finalize-edit');

new_photo_btn.onchange = (e)=>{
    pre_submit_edit_container.style.display = 'flex';
    pre_submit_edit_container.querySelector('#photo_edit_preview')
    let filesToLoad = new_photo_btn.files;
    previewFile('photo_edit_preview','new-photo-btn');
}

finalize_edit.onclick = (e)=>{
    photo_form.submit();
}

document.querySelectorAll('.selector-slide').forEach(item =>{
    item.onclick=(e)=>{
        let img_id = item.querySelector('img').id;
        document.querySelectorAll('.selector-slide').forEach(el =>{
            el.classList.remove('active-modal');
        });
        item.classList.add('active-modal');
        loadModal(img_id);
    }
});
function loadModal(index) {
    var preview = document.getElementById('preview_modal');
    var id_description_edit = document.getElementById('id_description_edit');
    var file = document.getElementById(index).src;
    var descr = document.getElementById(index).getAttribute('description');
    
    if (file) {
        preview.src = file;
        id_description_edit.value = descr;
    } else {
        preview.src = "";
        id_description_edit.value = '';
    }
}

document.querySelectorAll('.del-img').forEach(btn=>{
    btn.onclick=()=>{
        let prt=btn.parentElement.parentElement;
        let target_img_id = prt.getAttribute('photo_id');
        console.log(target_img_id);
        exePhoto(target_img_id,'del','house_photo');
        btn.parentElement.classList.remove('show-flex');
        prt.style.display = 'none'; 
        document.getElementById('preview_modal').src = "";
    }   
});
document.querySelectorAll('.sup2cover').forEach(btn=>{
    btn.onclick=()=>{
        let prt=btn.parentElement.parentElement;
        let target_img = prt.querySelector('img').src;
        let target_img_id = prt.getAttribute('photo_id');
        console.log(target_img_id);
        exePhoto(target_img_id,'cover','house_photo');
        btn.parentElement.classList.remove('show-flex');
    }   
});
function exePhoto(photo_id,request_type,desk){
    let wsStart = 'ws://';
    if(window.location.protocol == 'https'){
        wsStart = 'wss://';
    }
    let socket_url = wsStart + window.location.host + '/handle-photo/';
    let socket  = new WebSocket(socket_url);

    socket.onopen = async function(e){
        console.log('open',e);
        let data = {
            'photo_id':photo_id,
            'rqst_type':request_type,
            'desk':desk,
            'request_room':document.getElementById('ROOM_ID').value,
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
        make_toast(txt_feedback,'');
        socket.close();
    }
    socket.onclose = async function(e){
        console.log('close',e);
    }
    socket.onerror = async function(e){
        console.log('error',e);
    }
}