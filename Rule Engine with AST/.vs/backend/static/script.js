document.addEventListener("DOMContentLoaded", function() {
    const evaluateButton = document.getElementById("evaluate_btn");
    const resultDiv = document.getElementById("result");

    evaluateButton.addEventListener("click", function() {
        const rule = document.getElementById("rule").value.trim();
        const userData = document.getElementById("user_data").value.trim();

        // Clear previous results
        resultDiv.innerHTML = '';

        // Validate rule and user data
        if (!rule || !userData) {
            resultDiv.innerHTML = "Please fill in both fields.";
            return;
        }

        // Try to parse user data as JSON
        let parsedUserData;
        try {
            parsedUserData = JSON.parse(userData);
        } catch (e) {
            resultDiv.innerHTML = "Invalid JSON format in user data.";
            return;
        }

        // Make an AJAX request to the Flask backend
        fetch("/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ rule: rule, user_data: parsedUserData })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errorData => {
                    throw new Error("Network response was not ok: " + errorData.error);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = `Error: ${data.error}`;
            } else {
                resultDiv.innerHTML = `Eligible: ${data.eligible}`;
            }
        })
        .catch(error => {
            resultDiv.innerHTML = `Fetch error: ${error.message}`;
        });
    });
});
