// static/admin/js/form-validation.js

$(document).ready(function () {
    // Email format validation
    function isValidEmail(email) {
        const regex = /^\S+@\S+\.\S+$/;
        return regex.test(email);
    }

    // Phone number numeric validation
    function isNumeric(value) {
        return /^\d+$/.test(value);
    }

    // Function to validate required fields on keyup or blur
    function validateField(id, errorMsg, customCheck = null, customError = "") {
        const input = $("#" + id);
        const error = $("#error_" + id);

        input.on("keyup blur change", function () {
            const value = $(this).val().trim();
            if (!value) {
                error.text(errorMsg);
            } else if (customCheck && !customCheck(value)) {
                error.text(customError);
            } else {
                error.text("");
            }
        });
    }

    // Define fields and messages
    const fieldsToValidate = [
        { id: "title", msg: "Please select a title." },
        { id: "first_name", msg: "First name is required." },
        { id: "last_name", msg: "Last name is required." },
        { id: "gender", msg: "Please select a gender." },
        { id: "email", msg: "Email is required.", check: isValidEmail, err: "Enter a valid email address." },
        { id: "phone_no", msg: "Phone number is required.", check: isNumeric, err: "Only digits allowed." },
        { id: "address", msg: "Address is required." },
        { id: "country", msg: "Please select a country." },
        { id: "state", msg: "Please select a state." },
        { id: "city", msg: "City is required." },
        { id: "zipcode", msg: "Postal code is required.", check: isNumeric, err: "Only digits allowed." }
    ];

    // Attach validation handlers
    fieldsToValidate.forEach(field => {
        validateField(field.id, field.msg, field.check, field.err);
    });

    // Prevent text input in phone_no and zipcode
    $("#phone_no, #zipcode").on("input", function () {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // Validate again on submit
    $("#userForm").on("submit", function (e) {
        let hasError = false;

        fieldsToValidate.forEach(field => {
            const input = $("#" + field.id);
            const value = input.val().trim();
            const error = $("#error_" + field.id);

            if (!value) {
                error.text(field.msg);
                hasError = true;
            } else if (field.check && !field.check(value)) {
                error.text(field.err);
                hasError = true;
            } else {
                error.text("");
            }
        });

        if (hasError) {
            e.preventDefault();
            showToast("error", "Please correct the highlighted errors.");
        }
    });
});
