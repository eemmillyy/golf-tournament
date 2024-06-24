const button = document.querySelector('#buy_now_btn');
const button2 = document.querySelector('#buy_now_btn2');
const button3 = document.querySelector('#buy_now_btn3');
const button4 = document.querySelector('#buy_now_btn4');
const button5 = document.querySelector('#buy_now_btn5');
const button6 = document.querySelector('#buy_now_btn6');
const button7 = document.querySelector('#buy_now_btn7');
const button8 = document.querySelector('#buy_now_btn8');
const button9 = document.querySelector('#buy_now_btn9');
const button10 = document.querySelector('#buy_now_btn10');
const button11 = document.querySelector('#buy_now_btn11');
const button12 = document.querySelector('#buy_now_btn12');
const button13 = document.querySelector('#buy_now_btn13');

const handleStripePayment = (url) => {
    fetch(url)
    .then((result) => result.json())
    .then((data) => {
        var stripe = Stripe(data.checkout_public_key);
        stripe.redirectToCheckout({
            sessionId: data.checkout_session_id
        }).then((result) => {
            if (result.error) {
                console.error(result.error.message);
            }
        });
    })
    .catch((error) => {
        console.error('Error:', error);
    });
};

document.querySelectorAll('[id^="buy_now_btn"]').forEach(button => {
    button.addEventListener('click', event => {
        const url = `/stripe_pay${button.id.replace('buy_now_btn', '')}`;
        handleStripePayment(url);
    });
});