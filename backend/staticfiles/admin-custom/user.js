$(document).ready(function () {
    function showError(inputId, message) {
        $(`#error_${inputId}`).text(message);
    }

    function clearError(inputId) {
        $(`#error_${inputId}`).text('');
    }

    function validateField(id, message) {
        const value = $(`#${id}`).val().trim();
        if (!value) {
            showError(id, message);
            return false;
        } else {
            clearError(id);
            return true;
        }
    }

    function isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    function isValidPhone(phone) {
        const re = /^[0-9]{10,15}$/;
        return re.test(phone);
    }

    // Allow only numbers in phone fields
    $('#phone_no, #company_phone').on('input', function () {
        this.value = this.value.replace(/[^0-9]/g, '');
    });

    // Realtime validation
    $('#userForm input, #userForm select').on('blur change keyup', function () {
        const id = $(this).attr('id');
        const value = $(this).val().trim();

        switch (id) {
            case 'first_name':
                validateField(id, 'First name is required.');
                break;
            case 'last_name':
                validateField(id, 'Last name is required.');
                break;
            case 'email':
                if (!validateField(id, 'Email is required.')) break;
                if (!isValidEmail(value)) {
                    showError(id, 'Enter a valid email address.');
                } else {
                    clearError(id);
                }
                break;
            case 'phone_no':
                if (!validateField(id, 'Phone number is required.')) break;
                if (!isValidPhone(value)) {
                    showError(id, 'Enter a valid phone number (10-15 digits).');
                } else {
                    clearError(id);
                }
                break;
            case 'address':
            case 'title':
            case 'gender':
            case 'country':
            case 'state':
            case 'city':
            case 'zipcode':
            case 'group':
                validateField(id, `${id.replace('_', ' ')} is required.`);
                break;

            case 'seller_type':
                if ($('#sellerTypeFields').is(':visible')) {
                    validateField(id, 'Seller type is required.');
                }
                break;

            case 'company_name':
            case 'company_phone':
            case 'company_address':
            case 'company_country':
            case 'company_state':
            case 'company_city':
            case 'company_zipcode':
                if ($('#companySellerFields').is(':visible')) {
                    validateField(id, 'This field is required.');
                }
                break;
        }
    });

    // On submit
    $('#userForm').on('submit', function (e) {
        let valid = true;

        const requiredFields = [
            'title', 'first_name', 'last_name', 'gender',
            'email', 'phone_no', 'address', 'country', 'state', 'city', 'zipcode', 'group'
        ];

        for (const field of requiredFields) {
            if (!validateField(field, `${field.replace('_', ' ')} is required.`)) {
                valid = false;
            }
        }

        const emailVal = $('#email').val().trim();
        const phoneVal = $('#phone_no').val().trim();

        if (emailVal && !isValidEmail(emailVal)) {
            showError('email', 'Enter a valid email address.');
            valid = false;
        }

        if (phoneVal && !isValidPhone(phoneVal)) {
            showError('phone_no', 'Enter a valid phone number (10-15 digits).');
            valid = false;
        }

        if ($('#sellerTypeFields').is(':visible')) {
            if (!validateField('seller_type', 'Seller type is required.')) valid = false;
        }

        if ($('#companySellerFields').is(':visible')) {
            const companyFields = ['company_name', 'company_phone', 'company_address', 'company_country', 'company_state', 'company_city', 'company_zipcode'];
            for (const field of companyFields) {
                if (!validateField(field, `${field.replace('company_', '').replace('_', ' ')} is required.`)) {
                    valid = false;
                }
            }
        }

        if (!valid) {
            e.preventDefault();
        }
    });
});
