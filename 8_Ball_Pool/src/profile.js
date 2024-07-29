$(document).ready(function () {
    // Tooltip initialization
    $('[data-bs-toggle="tooltip"]').tooltip();

    var accountID = localStorage.getItem('accountID');
    var accountName = localStorage.getItem('accountName');

    if (!accountID || accountID < 0) {
        console.error("Account ID not found in localStorage.");
        return;
    }

    $('#profile').text(`${accountName} - Stats, Friends & More`);

    $('#friendsDropdown').on('click', function () {
        $.ajax({
            url: '/friendsList',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                // Handle friends list
                var friends = response.friends;

                var friendsList = $('#friendsList');
                friendsList.empty();

                if (friends.length === 0) {
                    friendsList.append(
                        `<li class="d-flex justify-content-between align-items-center">
                            No friends
                        </li>`
                    );
                } else {
                    friends.forEach(function (friend) {
                        friendsList.append(
                            `<li class="list-group-item d-flex justify-content-between align-items-center">${friend} 
                                <button class="gameInvite btn btn-primary" title="send game Invite">invite</button>
                                <button class="removeFriend btn btn-danger" title="remove from friend list">remove</button>
                            </li>`
                        );
                    });
                }

                $('.gameInvite').on('click', function () {


                });

                $('.removeFriend').on('click', function () {
                    var friendName = $(this).closest('li').contents().first().text().trim();
                    console.log('Remove friend: ', friendName);

                    var button = $(this);

                    $.ajax({
                        url: '/removeFriend',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            accountName: accountName,
                            friendName: friendName
                        }),
                        success: function (response) {
                            button.closest('li').remove();
                        },
                        error: function (response) {
                            console.error('Error removing friend:', response.message);
                        }
                    });
                });
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#statsDropdown').on('click', function () {
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
            success: function (response) {
                // Handle stats
                stats = response.stats
                let wins = 0;
                let loses = 0;
                let incomplete = 0;
                let totalGames = stats.length;

                var statsList = $('#statsList');
                statsList.empty();

                if (totalGames === 0) {
                    statsList.append('<li class="dropdown-item">No stats</li>');
                } else {
                    for (let i = 0; i < totalGames; i++) {
                        if (stats[i][1]) {
                            if (accountName == stats[i][1]) {
                                wins += 1;
                            } else {
                                loses += 1;
                            }
                        }
                    }
                    incomplete = totalGames - (wins + loses);

                    statsList.empty();
                    statsList.append(`<li class="dropdown-item text-success">${wins} Wins</li>`);
                    statsList.append(`<li class="dropdown-item text-danger">${loses} Losses</li>`);
                    statsList.append(`<li class="dropdown-item text-warning">${incomplete} Incomplete</li>`);
                }
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#sendFriendRequest').on('submit', function (event) {
        event.preventDefault();

        var friendName = $('#playerName').val();

        if (friendName === ''){
            alert("You need to put a player name");
            return;
        }

        if (friendName === accountName) {
            alert("You can't invite yourself");
            return;
        }

        $.ajax({
            url: '/friendInvite',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountName: String(accountName),
                accountID: parseInt(accountID),
                friendName: String(friendName)
            }),
            success: function (response) {
                let message = response.message;
                alert(message);
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    fetchNotifications(accountID);

    $('#notificationDropdownMenu').on('click', function () {
        fetchNotifications(accountID);
    });

    function fetchNotifications(accountID) {
        $.ajax({
            url: '/notificationlist',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                var notifications = response.notifications;
                var notificationList = $('.dropdown-menu.dropdown-menu-end');
                notificationList.empty();

                var recentNoti = notifications.filter(notification => notification[4] === 0).length;

                // Check if there are notifications
                if (notifications.length === 0) {
                    console.log(`count: ${notifications.length}`)
                    notificationList.append('<li class="dropdown-item">No new notifications</li>');
                } else {
                    notifications.forEach(function (notification) {
                        if (notification[3] === 2) {
                            if (notification[4] === 0) {
                                notificationList.append(
                                    `<li class="dropdown-item d-flex justify-content-between align-items-center notification-blue" data-id="${notification[0]}" data-friendid="${notification[1]}">
                                        ${notification[2]}
                                        <div>
                                            <button class="acceptInvite btn btn-primary" title="accept invite">Accept</button>
                                            <button class="declineInvite btn btn-danger" title="decline invite">Decline</button>
                                        </div>
                                    </li>`
                                );
                            } else {
                                notificationList.append(
                                    `<li class="dropdown-item d-flex justify-content-between align-items-center" data-id="${notification[0]}" data-friendid="${notification[1]}">
                                        ${notification[2]}
                                        <div>
                                            <button class="acceptInvite btn btn-primary" title="accept invite">Accept</button>
                                            <button class="declineInvite btn btn-danger" title="decline invite">Decline</button>
                                        </div>
                                    </li>`
                                );
                            }
                        } else {
                            if (notification[4] === 0) {
                                notificationList.append(
                                    `<li class="dropdown-item notification-blue" data-id="${notification[0]}">
                                        ${notification[2]}
                                    </li>`
                                );
                            } else {
                                notificationList.append(
                                    `<li class="dropdown-item" data-id="${notification[0]}">
                                        ${notification[2]}
                                    </li>`
                                );
                            }
                        }
                    });

                    $('.acceptInvite').on('click', function () {
                        var notificationID = $(this).closest('li').data('id');
                        var friendID = $(this).closest('li').data('friendid');
                        handleNotificationAction('acceptInvite', notificationID, accountID, friendID);
                        $(this).closest('li').remove();
                    });

                    $('.declineInvite').on('click', function () {
                        var notificationID = $(this).closest('li').data('id');
                        var friendID = $(this).closest('li').data('friendid');
                        handleNotificationAction('declineInvite', notificationID, accountID, friendID);
                        $(this).closest('li').remove();
                    });
                }

                // Update the notification number
                $('#notificationNumber').text(recentNoti);
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    }

    function handleNotificationAction(action, notificationID, accountID, friendID) {
        $.ajax({
            url: `/${action}`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID),
                friendID: parseInt(friendID),
                notificationID: parseInt(notificationID)
            }),
            success: function (response) {
                console.log(`${action} successful: `, response.message);
                fetchNotifications(accountID); // Refresh notifications to update the count
            },
            error: function (response) {
                console.error(`Error in ${action}: `, response.message);
            }
        });
    }

    $('#logOut').on('click', function () {

        $.ajax({
            url: '/logOut',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                if (response.status === 'Logged out successfully') {
                    console.log("Logged out successfully");

                    localStorage.removeItem('accountID');
                    localStorage.removeItem('accountName');
                    localStorage.removeItem('player1Name');
                    localStorage.removeItem('player2Name');
                    window.location.href = 'index.html';
                }
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#multiPlayer').on('click', function() {
        // Hide the buttons
        $('#multiPlayer').hide();
    
        // Show the form
        $('#multiPlayerForm').show();
        $('#player1').val(accountName)
    });

    $('#startGameForm').on('submit', function (event) {
        event.preventDefault();

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
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                if (response.status === 'Game Created successfully') {

                    const randomNumber = Math.random();
                    var PlayerTurn = randomNumber < 0.5 ? player1 : player2;

                    console.log("profile creates game good");
                    localStorage.setItem('gameID', response.gameID);
                    localStorage.setItem('player1Name', player1);
                    localStorage.setItem('player2Name', player2);
                    localStorage.setItem('gameName', response.gameName);
                    localStorage.setItem('PlayerTurn', PlayerTurn)

                    window.location.href = 'game.html';
                } else if (response.status === 'Error') {
                    console.error("Error: ", response.message);
                }
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });
});
