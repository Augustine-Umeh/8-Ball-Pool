$(document).ready(function () {

    $('#loginPage').text('Welcome back - 🎱 ball');

    $("#loginForm").on("submit", function (event) {
        event.preventDefault();
        
        var accountName = $("#accountName").val();
        var accountPassword = $("#accountPassword").val();


        $.ajax({
            url: '/verifyAccount',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountName: accountName,
                accountPassword: accountPassword
            }),
            success: function (response) {
                if (response.status === 'Account verified') {
                    localStorage.setItem('accountID', response.accountID);
                    localStorage.setItem('accountName', accountName);
                    console.log("login account", response.accountID);
                    window.location.href = '/profile.html';
                } else {
                    $("#message").text('Invalid account credentials. Please try again.');
                }
            },
            error: function () {
                $("#message").text('An error occurred. Please try again.');
            }
        });
    });
});
