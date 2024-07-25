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
    
});

