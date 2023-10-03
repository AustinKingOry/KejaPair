var like_btn = document.getElementById("like-btn");
if(like_btn){
    like_btn.onclick=(e)=>{
        let liked_by = document.getElementById('USER_ID').value;
        let room_id = like_btn.getAttribute('room-id');

        let wsStart = 'ws://';
        if(window.location.protocol == 'https'){
            wsStart = 'wss://';
        }
        let socket_url = wsStart + window.location.host + '/room/room-likes-handler/';
        let socket  = new WebSocket(socket_url);

        socket.onopen = async function(e){
            console.log('open',e);
            let data = {
                'room_id':room_id,
                'liked_by':liked_by,
            }
            data = JSON.stringify(data);
            socket.send(data);
        }
        socket.onmessage = async function(e){
            console.log('message',e);
            let data = JSON.parse(e.data);
            let feedback = data['feedback'];
            let reaction_type = data['reaction_type'];
            let total_likes = data['total_likes'];

            if(reaction_type==1){
                like_btn.querySelector('span').classList.replace('bi-heart','bi-heart-fill');
                like_btn.querySelector('span').classList.add('green-el');
                like_btn.querySelector('span').title = 'You like this room';
            }
            else{
                like_btn.querySelector('span').classList.replace('bi-heart-fill','bi-heart');
                like_btn.querySelector('span').classList.remove('green-el');
                like_btn.querySelector('span').title = 'Like This';
            }
            like_btn.querySelector('p').innerHTML = total_likes;
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
}

function showReviewForm(){
    document.getElementById('review-form-container').style.display='flex';
}

var ratingRange = document.getElementById('id_rating');
ratingRange.addEventListener('change',newRangeFunc);
function newRangeFunc(){
    var rangeValue = ratingRange.value;
    for (let i = 1; i <= rangeValue; i++) {
        if(document.getElementById('starBtn'.concat(i)).classList.contains('bi-star')){
            document.getElementById('starBtn'.concat(i)).classList.replace('bi-star','bi-star-fill');
        }
    }
    for (let i = 5; i > rangeValue; i--) {
        document.getElementById('starBtn'.concat(i)).classList.replace('bi-star-fill','bi-star');              
    }
    document.getElementById('rating-figures').innerHTML = rangeValue+' star(s)';
}
function starClick(starIndex){
    let ratingRange = document.getElementById('id_rating');
    rangeValue = parseInt(starIndex,10);
    ratingRange.value=rangeValue;
    for (let i = 1; i <= rangeValue; i++) {
        if(document.getElementById('starBtn'.concat(i)).classList.contains('bi-star')){
            document.getElementById('starBtn'.concat(i)).classList.replace('bi-star','bi-star-fill');
        }
    }
    for (let i = 5; i > rangeValue; i--) {
        document.getElementById('starBtn'.concat(i)).classList.replace('bi-star-fill','bi-star');              
    }
    document.getElementById('rating-figures').innerHTML = rangeValue+' star(s)';
}
//integration with openstreetmap
function initMap() {
    let coords = document.getElementById('map').getAttribute('data');
    const [latitude, longitude] = coords.split(',');
    // Convert the latitude and longitude to numbers
    const parsedLatitude = parseFloat(latitude);
    const parsedLongitude = parseFloat(longitude);
    const propertyLocation = [parsedLatitude, parsedLongitude];
    const map = L.map('map').setView(propertyLocation, 15);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  
    L.marker(propertyLocation).addTo(map)
        .bindPopup('Property Location')
        .openPopup();
}

// Call the initMap function when the window has finished loading
window.addEventListener('load',initMap);
  