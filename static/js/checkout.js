const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
paypal
  .Buttons({
    // Sets up the transaction when a payment button is clicked
    createOrder: function (data, actions) {
      return fetch("/api/orders/", {
        method: "post",
        headers: { "X-CSRFToken": csrftoken },
        mode: "same-origin",
      })
        .then((response) => response.json())
        .then((order) => order.id);
    },
    // Finalize the transaction after payer approval
    onApprove: function (data, actions) {
      return fetch(`/api/orders/${data.orderID}/capture/`, {
        method: "post",
        headers: { "X-CSRFToken": csrftoken },
        mode: "same-origin",
      })
        .then((response) => response.json())
        .then((orderData) => {
          const transaction = orderData.purchase_units[0].payments.captures[0];
          if (transaction.status === "COMPLETED") {
            location.href = "/checkout/thankyou/";
          } else {
            location.href = "/checkout/failed/";
          }
        })
        .catch((err) => console.error(err));
    },
  })
  .render("#paypal-button-container");

if (paypal.HostedFields.isEligible()) {
  let orderId;

  // Renders card fields
  paypal.HostedFields.render({
    // Call your server to set up the transaction
    createOrder: () => {
      return fetch("/api/orders/", {
        method: "post",
        headers: { "X-CSRFToken": csrftoken },
        mode: "same-origin",
      })
        .then((res) => res.json())
        .then((orderData) => {
          orderId = orderData.id; // needed later to complete capture
          return orderData.id;
        });
    },
    styles: {
      ".valid": {
        color: "green",
      },
      ".invalid": {
        color: "red",
      },
    },
    fields: {
      number: {
        selector: "#card-number",
        placeholder: "4111 1111 1111 1111",
      },
      cvv: {
        selector: "#cvv",
        placeholder: "123",
      },
      expirationDate: {
        selector: "#expiration-date",
        placeholder: "MM/YY",
      },
    },
  }).then((cardFields) => {
    document.querySelector("#card-form").addEventListener("submit", (event) => {
      event.preventDefault();
      cardFields
        .submit({
          // Cardholder's first and last name
          cardholderName: document.getElementById("card-holder-name").value,
          // Billing Address
          billingAddress: {
            // Street address, line 1
            streetAddress: document.getElementById(
              "card-billing-address-street"
            ).value,
            // Street address, line 2 (Ex: Unit, Apartment, etc.)
            extendedAddress: document.getElementById(
              "card-billing-address-unit"
            ).value,
            // State
            region: document.getElementById("card-billing-address-state").value,
            // City
            locality: document.getElementById("card-billing-address-city")
              .value,
            // Postal Code
            postalCode: document.getElementById("card-billing-address-zip")
              .value,
            // Country Code
            countryCodeAlpha2: document.getElementById(
              "card-billing-address-country"
            ).value,
          },
        })
        .then(() => {
          fetch(`/api/orders/${orderId}/capture/`, {
            method: "post",
            headers: { "X-CSRFToken": csrftoken },
            mode: "same-origin",
          })
            .then((res) => res.json())
            .then((orderData) => {
              // Two cases to handle:
              //   (1) Other non-recoverable errors -> Show a failure message
              //   (2) Successful transaction -> Show confirmation or thank you
              // This example reads a v2/checkout/orders capture response, propagated from the server
              // You could use a different API or structure for your 'orderData'
              const errorDetail =
                Array.isArray(orderData.details) && orderData.details[0];
              if (errorDetail) {
                let msg = "Sorry, your transaction could not be processed.";
                if (errorDetail.description)
                  msg += "\n\n" + errorDetail.description;
                if (orderData.debug_id) msg += " (" + orderData.debug_id + ")";
                return alert(msg); // Show a failure message
              }
              // Show a success message or redirect
              location.href = "/checkout/thankyou/";
            });
        })
        .catch((err) => {
          alert("Payment could not be captured! " + JSON.stringify(err));
        });
    });
  });
} else {
  // Hides card fields if the merchant isn't eligible
  document.querySelector("#card-form").style = "display: none";
}
