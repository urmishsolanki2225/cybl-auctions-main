$(document).ready(function () {
    function showError(inputId, message) {
        $('#error_' + inputId).text(message).show();
    }

    function clearError(inputId) {
        $('#error_' + inputId).text('').hide();
    }

    function isEmpty(value) {
        return $.trim(value) === '';
    }

    function validateField(inputId, required = true) {
        const value = $('#' + inputId).val();
        if (required && isEmpty(value)) {
            showError(inputId, 'This field is required');
            return false;
        } else {
            clearError(inputId);
            return true;
        }
    }

    // Seller Location validation fix
    function validateSellerLocation() {
        const selected = $('input[name="seller_location"]:checked').length > 0;
        if (!selected) {
            showError('seller_location', 'Please select seller location');
            return false;
        } else {
            clearError('seller_location');
            return true;
        }
    }

    // Keyup + Blur for fields
    $('#name, #description, #start_date, #lots_time_duration, #user, #address, #city, #zipcode').on('blur keyup', function () {
        validateField(this.id);
    });

    $('#country, #state').on('change blur', function () {
        validateField(this.id);
    });

    $('input[name="seller_location"]').on('change', function () {
        validateSellerLocation();
    });

    $('#auction-form').on('submit', function (e) {
        let valid = true;

        valid &= validateField('name');
        valid &= validateField('description');
        valid &= validateField('start_date');
        valid &= validateField('lots_time_duration');
        valid &= validateField('user');
        valid &= validateSellerLocation();

        const location = $('input[name="seller_location"]:checked').val();

        if (location === 'offsite') {
            valid &= validateField('address');
            valid &= validateField('country');
            valid &= validateField('state');
            valid &= validateField('city');
            valid &= validateField('zipcode');
        }

        if (!valid) {
            e.preventDefault();
            $('html, body').animate({
                scrollTop: $(".auction-form").offset().top - 100
            }, 300);
        }
    });

    // Hide seller location error initially
    clearError('seller_location');
});
