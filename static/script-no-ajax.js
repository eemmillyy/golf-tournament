var stripe = Stripe(checkout_public_key);

// Checkout buttons to select from
const button = document.querySelector('#buy_now_btn');
const button2 = document.querySelector('#buy_now_btn2');

// Function to handle the Stripe payment redirection with error catcher to alert the user if error occurs
const handleStripePayment = (sessionId) => {
    stripe.redirectToCheckout({
        sessionId: sessionId
    }).then(function (result) {
        if (result.error) {
            alert(result.error.message);
        }
    }).catch(function (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
};

// Event listener to the first button
button.addEventListener('click', function () {
    const sessionId = 'checkout_session_id'; // Checkout session ID
    handleStripePayment(sessionId);
});

// Event listener to the second button
button2.addEventListener('click', function () {
    const sessionId = 'checkout_session_id'; // Checkout session ID
    handleStripePayment(sessionId);
});