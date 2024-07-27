$(document).ready(function() {
    // Tooltip initialization
    $('[data-bs-toggle="tooltip"]').tooltip();

    $('#createGameForm').on('submit', function(event) {
        event.preventDefault();
        
        var accountID = localStorage.getItem('accountID');
        if (!accountID) {
            console.error("Account ID not found in localStorage.");
            return;
        }
        
        console.log("From Profile: ", accountID);
        var gameName = $('#gameName').val();
        var player1 = $('#player1').val();
        var player2 = $('#player2').val();
    
        $.ajax({
            url: '/startGame',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                gameName: gameName,
                p1Name: player1,
                p2Name: player2,
                accountID: parseInt(accountID) // Ensure accountID is sent as an integer
            }),
            success: function(response) {
                if (response.status === 'Game Created successfully') {
                    console.log("profile creates game good");
                    localStorage.setItem('gameID', response.gameID);
                    localStorage.setItem('player1Name', player1);
                    localStorage.setItem('player2Name', player2);
                    localStorage.setItem('gameName', response.gameName);
                    window.location.href = 'game.html';
                } else if (response.status === 'Error') {
                    console.error("Error: ", response.message);
                }
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#friendsList').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        if (!accountID) {
            console.error("Account ID not found in localStorage.");
            return;
        }
    
        // Toggle visibility of the friends list container
        var friendsListContainer = $('#friendsListContainer');
        if (friendsListContainer.hasClass('d-none')) {
            // Show friends list container
            $.ajax({
                url: '/friendsList',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 
                    accountID: parseInt(accountID) 
                }),
                success: function(response) {
                    // Handle friends list
                    var friends = response.friends;
                    console.log("Friends: ", friends);
    
                    // Populate friends list
                    var friendsList = $('#friendsList');
                    friendsList.empty();
                    friends.forEach(function(friend) {
                        friendsList.append(
                            `<li class="list-group-item">${friend} 
                                <button class="sendInvite btn btn-primary" title="send game Invite">Invite</button>
                                <button class="removeFriend btn btn-danger" title="remove from friend list">Remove</button>
                            </li>`
                        );
                    });
    
                    // Initialize tooltips
                    $('[data-bs-toggle="tooltip"]').tooltip();
    
                    // Show the container
                    friendsListContainer.removeClass('d-none');
                },
                error: function(response) {
                    console.error("Error: ", response.message);
                }
            });
        } else {
            // Hide friends list container
            friendsListContainer.addClass('d-none');
        }
    });    

    $('#sendFriendRequest').on('submit', function(event) {
        event.preventDefault();
        
        var accountID = localStorage.getItem('accountID');
        if (accountID < 0) {
            console.error("Account ID not found in localStorage.");
            return;
        }
        
        var accountName = localStorage.getItem('accountName');
        var friendName = $('#playerName').val();
    
        $.ajax({
            url: '/friendInvite',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountName: String(accountName),
                accountID: parseInt(accountID),
                friendName: String(friendName)
            }),
            success: function(response) {
                let message = response.message;
                alert(message);
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    });

    // Example usage for rejecting game invite
    $('#rejectGameInviteButton').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        var notificationID; 
        var friendName = $(this).closest('.list-group-item').text().trim().split(' ')[0];
        
        rejectInvite(notificationID, accountID, friendName, '/rejectGameInvite');
    });

    // Example usage for rejecting friend invite
    $('#rejectFriendInviteButton').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        var notificationID; 
        var friendName = $(this).closest('.list-group-item').text().trim().split(' ')[0];
        
        rejectInvite(notificationID, accountID, friendName, '/rejectFriendInvite');
    });

    function rejectInvite(notificationID, senderID, friendName, endpoint) {
        $.ajax({
            url: endpoint,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                notificationID: notificationID,
                accountID: senderID,
                friendName: friendName
            }),
            success: function(response) {
                console.log(response.status);
                updateNotificationCount();
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    }

    // Handle actions (Send Invite and Remove Friend)
    $('#sendInvite').on('click', function() {
        var friendName = $(this).closest('.list-group-item').text().trim().split(' ')[0]; 
        console.log("Send invite to:", friendName);

    });

    $('#removeFriend').on('click', function() {
        var friendName = $(this).closest('.list-group-item').text().trim().split(' ')[0]; 
        console.log("Remove friend:", friendName);

    });

    $('#statsDropdown').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        var accountName = localStorage.getItem('accountName')
        if (accountID < 0) {
            console.error("Account ID not found in localStorage.");
            return;
        }

        $.ajax({
            url: '/stats',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                accountID: parseInt(accountID)
            }),
            success: function(response) {
                // Handle stats
                stats = response.stats
                let wins = 0;
                let loses = 0;
                let incomplete = 0;
                let totalGames = stats.length;

                for (let i = 0; i < totalGames; i ++){
                    if (stats[i][1]) {
                        if (accountName == stats[i][1]) {
                            wins += 1;
                        } else {
                            loses += 1;
                        }
                    }
                }
                incomplete = totalGames - (wins + loses);
                
                var statsList = $('#statsList');
                statsList.empty();
                statsList.append(`<li class="dropdown-item text-success">${wins} Wins</li>`);
                statsList.append(`<li class="dropdown-item text-danger">${loses} Losses</li>`);
                statsList.append(`<li class="dropdown-item text-warning">${incomplete} Incomplete</li>`);
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    });

    function updateNotificationCount() {
        var accountID = localStorage.getItem('accountID');
        if (accountID < 0) {
            console.error("Account ID not found in localStorage.");
            return;
        }

        $.ajax({
            url: '/notificationlist',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                accountID: parseInt(accountID) 
            }),
            success: function(response) {
                let notification = response.notification
                console.log(`noti: ${notification}`)
                $('#notificationNumber').text(notification.length);
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    }
    updateNotificationCount()

    $('#notificationDropdownMenu').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        if (accountID < 0) {
            console.error("Account ID not found in localStorage.");
            return;
        }
    });

    $('#logOut').on('click', function() {
        var accountID = localStorage.getItem('accountID');
        if (accountID < 0) {
            console.error("Account ID not found in localStorage.");
            return;
        }

        $.ajax({
            url: '/logOut',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 
                accountID: parseInt(accountID) 
            }),
            success: function(response) {
                if (response.status === 'Logged out successfully') {
                    console.log("Logged out successfully");
                    
                    localStorage.removeItem('accountID');
                    window.location.href = 'index.html';
                }
            },
            error: function(response) {
                console.error("Error: ", response.message);
            }
        });
    });
});