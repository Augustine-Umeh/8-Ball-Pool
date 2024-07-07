$(document).ready(function() {
    $('#startGameForm').on('submit', function(e) {
        e.preventDefault(); // Prevent the default form submission

        // Collect form data
        var formData = {
            p1Name: $('#player1Name').val(), 
            p2Name: $('#player2Name').val(),
            gameName: $('#gameName').val(),
            accountID: $('#accountID').val()
        };

        // Store the player names in localStorage
        localStorage.setItem('player1Name', formData.p1Name);
        localStorage.setItem('player2Name', formData.p2Name);
        localStorage.setItem('gameName', formData.gameName);

        // Send a POST request to the server
        $.ajax({
            type: "POST",
            url: "/startGame",
            contentType: 'application/json', // Set the content type of the request
            data: JSON.stringify(formData), // Convert formData to a JSON string
            success: function(response) {
                // Handle success 
                console.log('Game started successfully:', response);
                window.location.href = 'game.html';
            },
            error: function(xhr, status, error) {
                // Handle error
                console.error('Error starting game:', error);
            }
        });

    });
});
