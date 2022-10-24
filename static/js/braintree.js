const bt_client = document.currentScript.getAttribute("data-braintree-token");
const bt_submit = document.getElementById("submit-button");
x = "";
braintree.dropin.create(
  {
    container: document.getElementById("dropin-container"),
    authorization: bt_client,
    card: {
      cardholderName: {
        required: false,
      },
    },
  },
  (error, Instance) => {
    bt_submit.addEventListener("click", () => {
      Instance.requestPaymentMethod((err, payload) => {
        fetch("/api/orders/braintree/", {
          method: "post",
          headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ payment_method_nonce: payload.nonce }),
          mode: "same-origin",
        })
          .then((result) => {
            if (result.ok) {
              location.href = "/checkout/thankyou/";
            } else {
              location.href = "/checkout/failed";
            }
          })
          .catch(() => {
            location.href = "/checkout/failed";
          });
      });
    });
  }
);
