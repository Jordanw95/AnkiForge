console.log('SANITY CHECK')

// new
// Get Stripe publishable key
fetch("http://127.0.0.1:8000/membership/config/")
.then((result) => { return result.json(); })
.then((data) => {
    // Initialize Stripe.js
    const stripe = Stripe(data.publicKey);
  
    // new
    // Event handler
    let submitBtn = document.querySelector("#submitbtn");
    if (submitBtn !== null) {
      submitBtn.addEventListener("click", () => {
      // Get Checkout Session ID
      fetch("http://127.0.0.1:8000/membership/create_checkout_session/")
        .then((result) => { return result.json(); })
        .then((data) => {
          console.log(data);
          // Redirect to Stripe Checkout
          return stripe.redirectToCheckout({sessionId: data.sessionId})
        })
        .then((res) => {
          console.log(res);
        });
      });
    }
  });