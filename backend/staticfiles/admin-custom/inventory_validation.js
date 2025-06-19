
$(document).ready(function () {
    function showError(field, message) {
        $('#error_' + field).text(message);
    }

    function clearError(field) {
        $('#error_' + field).text('');
    }

    function isEmpty(value) {
        return !value.trim();
    }

    function isPositiveNumber(value) {
        return /^\d+(\.\d+)?$/.test(value);
    }

    // Validate on blur or keyup
    $('#category').on('blur change', function () {
        if (isEmpty($(this).val())) showError('category', 'Category is required.');
        else clearError('category');
    });

    $('#title').on('keyup blur', function () {
        if (isEmpty($(this).val())) showError('title', 'Title is required.');
        else clearError('title');
    });
  
    $('#status').on('change blur', function () {
        if (isEmpty($(this).val())) showError('status', 'Status is required.');
        else clearError('status');
    });

    $('#condition').on('change blur', function () {
        if (isEmpty($(this).val())) showError('condition', 'Condition is required.');
        else clearError('condition');
    });

    $('#starting_bid').on('change blur', function () {
        if (isEmpty($(this).val())) showError('starting_bid', 'Starting bid is required.');
        else clearError('starting_bid');
    });

    $('#reserve_price').on('keyup blur', function () {
        const val = $(this).val().replace(/,/g, '');
        if (isEmpty(val)) showError('reserve_price', 'Reserve price is required.');
        else if (!isPositiveNumber(val)) showError('reserve_price', 'Enter a valid price.');
        else clearError('reserve_price');
    });

    $('#youtube_url').on('blur', function () {
        const val = $(this).val().trim();
        if (val && !/^https?:\/\/(www\.)?youtube\.com/.test(val)) {
            showError('youtube_url', 'Enter a valid YouTube URL.');
        } else {
            clearError('youtube_url');
        }
    });

    $('#in_transit_status').on('change blur', function () {
        if ($('#inTransitStatusDiv').is(':visible') && isEmpty($(this).val())) {
            showError('in_transit_status', 'In Transit Status is required.');
        } else {
            clearError('in_transit_status');
        }
    });

    $('#auction').on('change blur', function () {
        if ($('.auctionDiv').is(':visible') && isEmpty($(this).val())) {
            showError('auction', 'Auction is required.');
        } else {
            clearError('auction');
        }
    });


    $('#inventoryForm').on('submit', function (e) {
        // Optional: Add overall validation logic before AJAX
    });
});
