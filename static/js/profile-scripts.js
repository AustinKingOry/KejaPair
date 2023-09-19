let feed_categories = document.querySelectorAll('.feed-category-header');
feed_categories.forEach(feed_header => {
    feed_header.onclick=(e)=>{
        switch_feed_tabs(feed_header);
    }
})
var profile_feed_header = document.getElementById('profile_feed_header');
var rooms_feed_header = document.getElementById('rooms_feed_header');

function switch_feed_tabs(dom_item){
    document.querySelectorAll('.active_feed_header').forEach(ele=>{
        ele.classList.remove('active_feed_header');
    });
    dom_item.classList.add('active_feed_header');
    if(document.getElementById('rooms_feed_header').classList.contains('active_feed_header')){
        document.querySelectorAll('.rooms-feed-item').forEach(item=>{
            item.style.display='flex';
        });
        document.querySelectorAll('.profile-feed-item').forEach(item=>{
            item.style.display='none';
        });
    }
    else if(document.getElementById('profile_feed_header').classList.contains('active_feed_header')){
        document.querySelectorAll('.profile-feed-item').forEach(item=>{
            item.style.display='flex';
        });
        document.querySelectorAll('.rooms-feed-item').forEach(item=>{
            item.style.display='none';
        });
    }
    else{
        document.getElementById('rooms_feed_header').classList.add('active_feed_header');
        document.querySelectorAll('.rooms-feed-item').forEach(item=>{
            item.style.display='flex';
        });
    }
}