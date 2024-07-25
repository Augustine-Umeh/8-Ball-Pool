$(document).ready(function () {
    $("#signupForm").on("submit", function (event) {
        event.preventDefault();
        
        var accountName = $("#accountName").val();
        var accountPassword = $("#accountPassword").val();

        $.ajax({
            url: '/createAccount',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                accountName: accountName,
                accountPassword: accountPassword
            }),
            success: function (response) {
                if (response.status === 'Account created successfully') {
                    localStorage.setItem('accountID', response.accountID);
                    localStorage.setItem('accountName', accountName);
                    console.log("signup account", response.accountID);
                    window.location.href = 'profile.html';
                } else if (response.status === 'Account already exists'){
                    $("#message").text('Account already exists, Redirecting to login...');
                    window.location.href = 'login.html';
                }
            },
            error: function () {
                $("#message").text('An error occurred. Please try again.');
            }
        });
    });
});
