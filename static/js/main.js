function previewFile(sectId,photoId,fileSize) {
    var preview = document.getElementById(sectId);
    var file    = document.getElementById(photoId).files[0];
    var reader  = new FileReader();
    if(fileSize != null){
        f_size = parseInt(fileSize);
    }
    else{
        f_size = 10;
    }

    if(file.size > 1024*1024*f_size){
        alert("File is too big!");
        document.getElementById(photoId).value = "";
        return false;
    }
    else{
        reader.onloadend = function () {
            preview.src = reader.result;
        }

        if (file) {
            reader.readAsDataURL(file);
        } else {
            preview.src = "";
        }
        return true;
    }
}
function showPreview(holder_id,image_field,input_field,size){
    let p = new Promise((resolve,reject)=>{
        let preview_set = previewFile(image_field,input_field,size);
        if(preview_set==true){
            resolve('file has been successfully added!');
        }
        else{
            reject('failed. Try again.');
        }
    });
    p.then((message)=>{
        document.getElementById(image_field).classList.remove('hidden');
        document.getElementById(holder_id).classList.add('hidden');
        make_toast(message,true);
    }).catch((message)=>{
        make_toast(message,false);
    });
}

document.body.addEventListener('click',function(e){
    if(e.target.classList.contains('bgPopUpWrapper') || e.target.classList.contains("cancelBgPopUpWrapper")){
        let popupbgs= document.querySelectorAll('.bgPopUpWrapper');
        popupbgs.forEach(popupbg => {
            if(popupbg.classList.contains('show-flex')){
                popupbg.classList.remove('show-flex');
            }
            popupbg.style.display='none';
            popupbg.style.display=null;
            
        });
    }
})



$("body").click
(
function(e)
{
    if($(".drop-list").css('display') === 'flex'){
        if(!e.target.classList.contains("drop-list")){
            $(".drop-list").css("display", "none");
        }
    }
    else if($(".drop-list").css('display') === 'none'){
        if(e.target.classList.contains("nav-links")||e.target.classList.contains('acc-link')||e.target.classList.contains('drop-btn')){
            $(".drop-list").css("display", "flex");
        }
    }
}
);


var swiper = new Swiper(".mySwiper", {
    slidesPerView: 1,
    grabCursor: true,
    loop: false,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
    navigation: {
        nextEl: ".next-slide",
        prevEl: ".prev-slide",
    },
});


var actionBtns=document.querySelectorAll('.actions-btn');
var actionWrappers=document.querySelectorAll('.actions-sect');
var dropable_containers=document.querySelectorAll('.dropable-container');
var dropdownBtns=document.querySelectorAll('.dropable-controller');
var dropable_body=document.querySelectorAll('.dropable-sect');
window.addEventListener('load',()=>{
    for(i=0;i<actionBtns.length;i++){
        actionBtns[i].setAttribute('onclick','hideActionsWrapper(\''+i+'\')')
    }
    for(i=0;i<dropdownBtns.length;i++){
        dropdownBtns[i].setAttribute('onclick','expandCardWrapper(\''+i+'\')')
    }
});

function hideActionsWrapper(index){
    actionWrappers[index].classList.toggle('show-flex');
}
function expandCardWrapper(index){
    dropable_body[index].classList.toggle('hidden');
    dropable_containers[index].style.minHeight="fit-content";
    dropdownBtns[index].classList.toggle('bi-chevron-up');
    if(dropdownBtns[index].classList.contains('bi-chevron-up')){
        dropdownBtns[index].setAttribute('data-tool-tip','Maximize');
        dropdownBtns[index].setAttribute('title','Maximize');
    }
    else if(dropdownBtns[index].classList.contains('bi-chevron-down')){
        dropdownBtns[index].setAttribute('data-tool-tip','Minimize');
        dropdownBtns[index].setAttribute('title','Minimize');
    }
}


function make_toast(text,status){
    let toast_wrapper = document.getElementById('toast-wrapper');
    if(toast_wrapper){
        let toast_icon=toast_wrapper.querySelector('.info-type');
        if(status==true){
            toast_icon.classList.replace('bi-info-circle','bi-check-circle-fill');
            toast_icon.style.color='var(--bgGreen2)';
            // toast_icon.style.color='var(--fontWhite)';
        }
        else if(status==false){
            toast_icon.classList.replace('bi-info-circle','bi-exclamation-triangle-fill');
            toast_icon.style.color='red';
            // toast_icon.style.color='var(--fontWhite)';
        }
        toast_wrapper.style.display = 'flex';
        let toast_message = document.getElementById('toast-message');
        toast_message.innerHTML = text;
    }
    let time_out_progress = document.getElementById('time-out-progress');
    animate_progress(time_out_progress);        
}
// toasts by sweetalert2
function alertMessage(tag,message){
	Swal.fire({
		title: tag+'!',
		text: message,
		icon: tag,
		confirmButtonText: 'Ok'
	});
}
const makeToast=(icon,title)=>{
	const Toast = Swal.mixin({
		toast: true,
		position: 'bottom-end',
		showConfirmButton: false,
		timer: 3000,
		timerProgressBar: true,
		didOpen: (toast) => {
		  toast.addEventListener('mouseenter', Swal.stopTimer)
		  toast.addEventListener('mouseleave', Swal.resumeTimer)
		}
	  })
	  
	  Toast.fire({
		icon: icon,
		title: title
	  });
}
function makeTimerToast(){
	let timerInterval
	Swal.fire({
	title: 'Auto close alert!',
	html: 'I will close in <b></b> milliseconds.',
	timer: 2000,
	timerProgressBar: true,
	didOpen: () => {
		Swal.showLoading()
		const b = Swal.getHtmlContainer().querySelector('b')
		timerInterval = setInterval(() => {
		b.textContent = Swal.getTimerLeft()
		}, 100)
	},
	willClose: () => {
		clearInterval(timerInterval)
	}
	}).then((result) => {
	/* Read more about handling dismissals below */
	if (result.dismiss === Swal.DismissReason.timer) {
		console.log('I was closed by the timer')
	}
	})
}
function makeConfirmationToast(){
	const swalWithBootstrapButtons = Swal.mixin({
		customClass: {
		  confirmButton: 'btn btn-success',
		  cancelButton: 'btn btn-danger'
		},
		buttonsStyling: true
	  })
	  
	  swalWithBootstrapButtons.fire({
		title: 'Are you sure?',
		text: "You won't be able to revert this!",
		icon: 'warning',
		showCancelButton: true,
		confirmButtonText: 'Yes, delete it!',
		cancelButtonText: 'No, cancel!',
		reverseButtons: true
	  }).then((result) => {
		if (result.isConfirmed) {
		  swalWithBootstrapButtons.fire(
			'Deleted!',
			'Your file has been deleted.',
			'success'
		  )
		} else if (
		  /* Read more about handling dismissals below */
		  result.dismiss === Swal.DismissReason.cancel
		) {
		  swalWithBootstrapButtons.fire(
			'Cancelled',
			'Your imaginary file is safe :)',
			'error'
		  )
		}
	  })
}

function animate_progress(ele){
    let width = 100,i=0;
    if(i==0){
        i=1;
        var id = setInterval(() => {
            if(width<=0){
                clearInterval(id);
                i=0;
            }
            else{
                width--;
                ele.style.width = width+'%';
            }
            if(width<=0){
                ele.parentElement.style.display = 'none';
            }
        }, 40);
    }    
}


document.querySelectorAll('.filter-field').forEach(field=>{
    let field_id = field.id;
    field.onchange = () => filter_rooms(field_id);
});
function filter_rooms(field){
    let field_value = document.getElementById(field).value;
    let rooms_container = document.getElementById('rooms-container-main');
    let all_rooms = rooms_container.querySelectorAll('.room-card');
    all_rooms.forEach(room=>{
        let room_rent = parseInt(room.getAttribute('rent'));
        let room_location = room.getAttribute('loc');
        let room_gender = room.querySelector('.host-gender').innerHTML;
        let room_capacity = parseInt(room.getAttribute('capacity'));
            
        if((field).toLowerCase() == 'locationfilter'){
            if((field_value).toLowerCase()!=(room_location).toLowerCase()){
                room.style.display = 'none';
            }
            // else if((field_value).toLowerCase()==(room_location).toLowerCase()){
            //     room.style.display = 'flex';
            // }
            // else{
            //     room.style.display = 'flex';
            // }
        }
        else if((field).toLowerCase() == 'rentfilter'){
            if(parseInt(field_value)<room_rent){
                room.style.display = 'none';
            }
            // else if(parseInt(field_value)>=room_rent){
            //     room.style.display = 'flex';
            // }
            // else{
            //     room.style.display = 'flex';
            // }
        }
        else if((field).toLowerCase() == 'genderfilter'){
            if(field_value!=room_gender){
                room.style.display = 'none';
            }
            // else if(field_value==room_gender){
            //     room.style.display = 'flex';
            // }
            // else{
            //     room.style.display = 'flex';
            // }
        }
        else if((field).toLowerCase() == 'capacityfilter'){
            if(field_value!=room_capacity){
                room.style.display = 'none';
            }
            // else if(field_value==room_capacity){
            //     room.style.display = 'flex';
            // }
            // else{
            //     room.style.display = 'flex';
            // }
        }

        if(field_value=='*'){
            room.style.display='flex';
        }
    });

}

if(document.getElementById('nav-toggle')!=null){
    window.addEventListener('load',checkLiveData);
}

function checkLiveData(){
    let nav_notif_badge = document.getElementById('global-side-nav').querySelector('.notif-alert');
    let nav_chat_badge = document.getElementById('global-side-nav').querySelector('.chats-alert');
    let nav_pairs_badge = document.getElementById('global-side-nav').querySelector('.pairs-alert');
    let nav_matches_badge = document.getElementById('global-side-nav').querySelector('.matches-alert');
    let nav_alert_badge = document.getElementById('global-side-nav').querySelector('.alerts-icon');

    let wsStart = 'ws://';
    if(location.protocol == 'https'){
        wsStart = 'wss://';
    }
    let nav_socket_url = wsStart + window.location.host + '/live-updates/';
    let nav_socket  = new WebSocket(nav_socket_url);

    nav_socket.onopen = async function(e){
        // console.log('open',e);
        let data = {
            'rqst_type':'*',
            'request_user':document.getElementById('nav-toggle').querySelector('.l-u-name').getAttribute('user-id'),
        }
        data = JSON.stringify(data);
        // setInterval(() => {
        nav_socket.send(data);
        // }, 5000);
        nav_socket.send(data);
    }
    nav_socket.onmessage = async function(e){
        // console.log('message',e);
        let data = JSON.parse(e.data);
        let total_count = data['total_count'];
        let notif_count = data['notif_count'];
        let pairs_count = data['pairs_count'];
        let matches_count = data['pairs_count'];
        let chats_count = data['chats_count'];
        let status = data['status'];

        if(notif_count>0){nav_notif_badge.innerHTML = notif_count}
        if(chats_count>0){nav_chat_badge.innerHTML = chats_count}
        if(pairs_count>0 && nav_pairs_badge){nav_pairs_badge.innerHTML = pairs_count}
        if(matches_count>0 && nav_matches_badge){nav_matches_badge.innerHTML = matches_count}
        // let txt_feedback = feedback;
        // make_toast(txt_feedback,status);
        // nav_socket.close();
        return status;
    }
    nav_socket.onclose = async function(e){
        // console.log('close',e);
    }
    nav_socket.onerror = async function(e){
        // console.log('error',e);
    }
}

let side_nav_toggle = document.getElementById('side-nav-toggle');
let sidenav = document.getElementById('global-side-nav');
// window.addEventListener('load',toggle_aside);
side_nav_toggle.onclick=(e)=>{
    toggle_aside();
}
function toggle_aside(){
    // let links = sidenav.querySelectorAll('.side-nav-link');
    // links.forEach(link=>{
    //     if(link.classList.contains('hidden')){
    //         link.classList.remove('hidden');
    //         link.parentElement.style.width='100%';
    //         link.parentElement.style.padding='unset';
    //         link.previousElementSibling.style.width='unset';
    //         link.parentElement.parentElement.style.minWidth='250px';
    //         sidenav.querySelector('.icons-container').style.width=null;
    //         sidenav.querySelector('.icons-container').style.padding=null;
    //         sidenav.style.width='300px';
    //         side_nav_toggle.classList.replace('bi-list','bi-x');
    //     }
    //     else if(!link.classList.contains('hidden')){
    //         link.classList.add('hidden');
    //         link.parentElement.style.width='0px';
    //         link.parentElement.style.padding='0px';
    //         link.previousElementSibling.style.width='0';
    //         link.parentElement.parentElement.style.minWidth='unset';
    //         sidenav.querySelector('.icons-container').style.width='0px';
    //         sidenav.querySelector('.icons-container').style.padding='0';
    //         sidenav.style.width='fit-content';
    //     }
    // });
    if(sidenav.classList.contains('show-flex')){
        sidenav.classList.remove('show-flex');
        side_nav_toggle.classList.replace('bi-x','bi-list');
    }
    else{
        sidenav.classList.add('show-flex');
        side_nav_toggle.classList.replace('bi-list','bi-x');
    }
}
window.addEventListener('load',()=>{
	if (document.querySelectorAll('.backend-message')){
		let messages = document.querySelectorAll('.backend-message');
		messages.forEach(m=>{
			let message=m.getAttribute('message_text');
			let tags=m.getAttribute('message_tags');
			// alertMessage(tags,message);
			makeToast(tags,message);
		});
	}
});

function displayLocation(latitude, longitude) {
    // Set the values of the hidden input fields
    document.getElementById('id_maps_link').value = latitude+","+longitude;
    document.getElementById('map').classList.toggle('hidden');
  
    // Display the location on the map
    const map = L.map('map').setView([latitude, longitude], 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  
    L.marker([latitude, longitude]).addTo(map)
        .bindPopup('Your Location')
        .openPopup();
}
  
  
function getUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;
            console.log(latitude,longitude);
            displayLocation(latitude, longitude);
        },
        (error) => {
            alert('Error getting your location: ' + error.message);
        }
      );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
}  
    