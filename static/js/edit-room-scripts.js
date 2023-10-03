var edit_btn = document.getElementById('show-room-form');
edit_btn.onclick=(e)=>{
    document.getElementById('room-data-form').classList.add('show-flex');
}
function deleteProperty(propertyId) {
    return new Promise((resolve, reject) => {
        if (!propertyId) {
            reject('Invalid property id. Try again.');
            return;
        }

        let wsStart = 'ws://';
        if (location.protocol === 'https:') {
            wsStart = 'wss://';
        }
        let socket_url = wsStart + window.location.host + '/delete-room/';
        let socket = new WebSocket(socket_url);

        socket.onopen = function () {
            console.log('WebSocket connected');

            const data = {
                action: 'delete_property',
                property_id: propertyId
            };
            socket.send(JSON.stringify(data));
        };

        socket.onmessage = function (event) {
            const message = JSON.parse(event.data);
            console.log('Received message:', message);
            if (message.bool) {
                resolve(message);
            } else {
                reject(message);
            }
        };
        
        // Handle WebSocket state change
        socket.onclose = function (event) {
            console.log('WebSocket closed:', event);
            reject('WebSocket closed before response.');
        };
    });
}
function toggleListing(propertyId) {
    return new Promise((resolve, reject) => {
        if (!propertyId) {
            reject('Invalid property id. Try again.');
            return;
        }

        let wsStart = 'ws://';
        if (location.protocol === 'https:') {
            wsStart = 'wss://';
        }
        let socket_url = wsStart + window.location.host + '/remove-listing/';
        let socket = new WebSocket(socket_url);

        socket.onopen = function () {
            console.log('WebSocket connected');

            const data = {
                action: 'remove_listing',
                property_id: propertyId
            };
            socket.send(JSON.stringify(data));
        };

        socket.onmessage = function (event) {
            const message = JSON.parse(event.data);
            console.log('Received message:', message);
            if (message.bool) {
                resolve(message);
            } else {
                reject(message);
            }
        };
        
        // Handle WebSocket state change
        socket.onclose = function (event) {
            console.log('WebSocket closed:', event);
            reject('WebSocket closed before response.');
        };
    });
}

function confirmDeletionToast(id) {
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: 'btn btn-success',
            cancelButton: 'btn btn-danger'
        },
        buttonsStyling: true
    });

    swalWithBootstrapButtons.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Proceed',
        cancelButtonText: 'Cancel',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            const confirmBtn = Swal.getConfirmButton();
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing';
            confirmBtn.disabled = true;

            deleteProperty(id)
                .then((response) => {
                    swalWithBootstrapButtons.fire(
                        'Deleted!',
                        response.message,
                        'success'
                    ).then(() => {
                        // Redirect to 'my-rooms'
                        window.location.href = '/my-rooms/';
                    });
                })
                .catch((error) => {
                    swalWithBootstrapButtons.fire(
                        'Error!',
                        error.message,
                        'warning'
                    );
                })
                .finally(() => {
                    confirmBtn.innerHTML = 'Proceed';
                    confirmBtn.disabled = false;
                });
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            swalWithBootstrapButtons.fire(
                'Cancelled',
                'You have cancelled this deletion.',
                'error'
            );
        }
    });
}

function toggleListingToast(id) {
    const swalWithBootstrapButtons = Swal.mixin({
        customClass: {
            confirmButton: 'btn btn-success',
            cancelButton: 'btn btn-danger'
        },
        buttonsStyling: true
    });

    swalWithBootstrapButtons.fire({
        title: 'Are you sure?',
        text: "This action can be reversed at any time.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Proceed',
        cancelButtonText: 'Cancel',
        reverseButtons: true
    }).then((result) => {
        if (result.isConfirmed) {
            const confirmBtn = Swal.getConfirmButton();
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing';
            confirmBtn.disabled = true;

            toggleListing(id)
                .then((response) => {
                    swalWithBootstrapButtons.fire(
                        'Sucess!',
                        response.message,
                        'success'
                    );
                })
                .catch((error) => {
                    swalWithBootstrapButtons.fire(
                        'Error!',
                        error.message,
                        'warning'
                    );
                })
                .finally(() => {
                    confirmBtn.innerHTML = 'Proceed';
                    confirmBtn.disabled = false;
                });
        } else if (result.dismiss === Swal.DismissReason.cancel) {
            swalWithBootstrapButtons.fire(
                'Cancelled',
                'You have cancelled this process.',
                'error'
            );
        }
    });
}