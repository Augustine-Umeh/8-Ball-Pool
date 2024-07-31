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
                    statsList.append('<li class="dropdown-item non-clickable">No stats</li>');
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
                    statsList.append(`<li class="dropdown-item text-success non-clickable">${wins} Wins</li>`);
                    statsList.append(`<li class="dropdown-item text-danger non-clickable">${loses} Losses</li>`);
                    statsList.append(`<li class="dropdown-item text-warning non-clickable">${incomplete} Incomplete</li>`);
                }
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#friendsDropdown').on('click', function () {
        $.ajax({
            url: '/friendsList',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                var friends = response.friends;
                var friendsList = $('#friendsList');
                friendsList.empty();

                if (friends.length === 0) {
                    friendsList.append(
                        `<li class="d-flex justify-content-center align-items-center non-clickable">
                            <h2 class="mt-5 mb-4">No friends😢</h2>
                        </li>`
                    );
                } else {
                    friendsList.append('<h2 class="mt-4">Friends</h2>');
                    friends.forEach(function (friend) {
                        let statusIcon, statusText;
                        switch (friend[1]) {
                            case 1:
                                statusIcon = './assets/8-Ball-AI-online.svg';
                                statusText = 'Online';
                                break;
                            case 2:
                                statusIcon = './assets/8-Ball-AI-inGame.svg';
                                statusText = 'In Game';
                                break;
                            default:
                                statusIcon = './assets/8-Ball-AI-offline.svg';
                                statusText = 'Offline';
                        }

                        friendsList.append(
                            `<li class="list-group-item friend-drop">
                                <div class="d-flex justify-content-between align-items-center friend-and-button">
                                    <span class="friend-name">${friend[0]}</span>
                                    <div class="mt-4">
                                        <button class="gameInvite btn btn-primary btn-sm" title="send game invite">Invite</button>
                                        <button class="removeFriend btn btn-danger btn-sm" title="remove from friends list">Remove</button>
                                    </div>
                                </div>
                                <div class="d-flex align-items-center friend-status">
                                    <img src="${statusIcon}" alt="${statusText}" width="20" height="20" class="me-2" />
                                    <p class="mb-0">${statusText}</p>
                                </div>
                            </li>`
                        );
                    });
                }

                $('.gameInvite').on('click', function () {
                    // Handle game invite functionality
                });

                $('.removeFriend').on('click', function () {
                    var friendName = $(this).closest('li').find('.friend-name').text().trim();
                    var button = $(this);

                    $('body').addClass('blur-background');
                    $('#actionChecker').show();
                    $('#actionCheckerText').text(`Are you sure you want to remove ${friendName}`)

                    $('#confirmAction').on('click', function () {
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
                                $('#actionChecker').hide();
                                $('body').removeClass('blur-background');
                            },
                            error: function (response) {
                                console.error('Error removing friend:', response.message);
                                $('#actionChecker').hide();
                                $('body').removeClass('blur-background');
                            }
                        });
                    });

                    $('#cancelAction').on('click', function () {
                        $('#actionChecker').hide();
                        $('body').removeClass('blur-background');
                    });
                });
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    });

    $('#sendFriendRequest').on('submit', function (event) {
        event.preventDefault();

        var friendName = $('#playerName').val();

        if (friendName === '') {
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

    $('#notificationDropdownMenu').on('click', function (event) {
        event.stopPropagation();
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

                const timestamp = new Date().toLocaleString(); // Get current date and time as a readable string

                // Check if there are notifications
                if (notifications.length === 0) {
                    notificationList.append('<li class="list-group-item justify-content-center noti_drop non-clickable">No new notifications</li>');
                } else {
                    notifications.forEach(function (notification, index) {
                        if (notification[3] === 2) {
                            if (notification[4] === 0) {
                                notificationList.append(
                                    `<li class="list-group-item noti_drop d-flex justify-content-between align-items-center notification-blue" data-id="${notification[0]}" data-friendid="${notification[1]}">
                                        ${notification[2]}
                                        <div>
                                            <button class="acceptInvite btn btn-primary btn-sm" title="accept invite">Accept</button>
                                            <button class="declineInvite btn btn-danger btn-sm" title="decline invite">Decline</button>
                                        </div>
                                    </li>`
                                );
                            } else {
                                notificationList.append(
                                    `<li class="list-group-item noti_drop d-flex justify-content-between align-items-center" data-id="${notification[0]}" data-friendid="${notification[1]}">
                                        ${notification[2]}
                                        <div>
                                            <button class="acceptInvite btn btn-primary btn-sm" title="accept invite">Accept</button>
                                            <button class="declineInvite btn btn-danger btn-sm" title="decline invite">Decline</button>
                                        </div>
                                    </li>`
                                );
                            }
                        } else {
                            if (notification[4] === 0) {
                                notificationList.append(
                                    `<li class="list-group-item noti_drop notification-blue non-clickable" data-id="${notification[0]}">
                                        ${notification[2]}
                                    </li>`
                                );
                            } else {
                                notificationList.append(
                                    `<li class="list-group-item noti_drop non-clickable" data-id="${notification[0]}">
                                        ${notification[2]}
                                    </li>`
                                );
                            }
                        }

                        // Add a divider after each item except the last one
                        if (index < notifications.length - 1) {
                            notificationList.append('<hr class="dropdown-divider">');
                        }
                    });

                    $('.acceptInvite').on('click', function (event) {
                        event.stopPropagation();

                        var notificationID = $(this).closest('li').data('id');
                        var friendID = $(this).closest('li').data('friendid');

                        handleNotificationAction('acceptInvite', notificationID, accountID, friendID);
                        $(this).closest('li').remove();
                    });

                    $('.declineInvite').on('click', function (event) {
                        event.stopPropagation();

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

        $('body').addClass('blur-background');
        $('#actionChecker').show();
        $('#actionCheckerText').text(`Are you sure you want to Log out`);

        $('#confirmAction').on('click', function () {
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

        $('#cancelAction').on('click', function () {
            $('#actionChecker').hide();
            $('body').removeClass('blur-background');
        });
    });

    $('#multiPlayer').on('click', function () {
        $('body').addClass('blur-background');
        $('#multiPlayerForm').show();
        $('#player1').val(accountName)

        $('#cancelIcon').on('click', function () {
            $('body').removeClass('blur-background');
            $('#multiPlayerForm').hide();
        });

        $('#startGameForm').on('submit', function (event) {
            event.preventDefault();
            $('#multiPlayerForm').hide();
            $('body').removeClass('blur-background');

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

    retrieveGameHistory();
    function retrieveGameHistory() {
        $.ajax({
            url: '/retrieveGames',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountID: parseInt(accountID)
            }),
            success: function (response) {
                var historyContent = $('#historyContent');
                historyContent.empty();

                var tables = response.tables;

                if (tables.length === 0) {
                    historyContent.append('<h1 class="history-text">No Game History</h1>');
                } else {
                    tables.forEach(function (table) {
                        var gameName = table[0];
                        var player1 = table[1];
                        var player2 = table[2];
                        var tableSVG = table[3];
                        var player1Category = table[4];
                        var gameUsed = table[5];
                        var winner = table[6];
                        var recap = 1;

                        var player1Balls = '';
                        var player2Balls = '';

                        if (player1Category) {
                            if (player1Category === 'stripe') {
                                player1Balls = '<img id="playerBalls" src="./assets/8-Ball-AI-LowBalls.svg" alt="Low Balls">';
                                player2Balls = '<img id="playerBalls" src="./assets/8-Ball-AI-HighBalls.svg" alt="High Balls">';
                            } else {
                                player1Balls = '<img id="playerBalls" src="./assets/8-Ball-AI-HighBalls.svg" alt="High Balls">';
                                player2Balls = '<img id="playerBalls" src="./assets/8-Ball-AI-LowBalls.svg" alt="Low Balls">';
                            }
                        }

                        var svgContent = tableSVG
                            ? `<div class="game-svg-container">
                                    <div class="game-svg">${tableSVG}</div>
                                    <div class="gameInfo">
                                        <h2 class="gameName">${gameName}</h2><br>
                                        <div class="d-flex player-names-container">
                                            <h5 class="PlayerNames">Player 1: ${player1}</h5><br>
                                            ${player1Balls}
                                            <h5 class="PlayerNames">Player 2: ${player2}</h5><br>
                                            ${player2Balls}
                                        </div>
                                        ${gameUsed === 2 ? `${winner} won this game` : 
                                        `${recap ? `<p class="text-center mt-1">Recap: ${recap}</p>` : ''}
                                        <h5 class="text-center mt-3">Player Turn: </h5>
                                        <p class="text-center">Click to continue this game</p><br>
                                        <div class="text-center">
                                            <button id="continueGame" class="btn btn-success">Yes</button>
                                        </div>`}
                                    </div>
                                </div>`
                            : '';

                        var gameHistoryItem = `
                            <div class="game-history-item">
                                ${svgContent}
                            </div>
                        `;
                        historyContent.append(gameHistoryItem);
                    });

                }
            },
            error: function (response) {
                console.error("Error: ", response.message);
            }
        });
    }
});
