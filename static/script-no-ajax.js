var stripe = Stripe(checkout_public_key);

const button = document.querySelector('#buy_now_btn');
const button = document.querySelector('#buy_now_btn2');

button.addEventListener('click', event => {
    stripe.redirectToCheckout({
        // Make the id field from the Checkout Session creation API response
        // available to this file, so you can provide it as parameter here
        // instead of the {{CHECKOUT_SESSION_ID}} placeholder.
        sessionId: checkout_session_id
    }).then(function (result) {
        // If `redirectToCheckout` fails due to a browser or network
        // error, display the localized error message to your customer
        // using `result.error.message`.
    });
})

document.querySelector("#checkout-button").addEventListener("click", function () {
    const stripe = Stripe('your-publishable-key-here'); // Replace with actual publishable key
    const sessionId = 'your-session-id-here'; // Replace with actual session ID

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
});