$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_date").val(res.date);
        $("#order_total").val(res.total);
        $("#order_payment").val(res.payment);
        $("#order_address").val(res.address);
        $("#order_customer_id").val(res.customer_id);
        $("#order_status").val(res.status);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_id").val("");
        $("#order_date").val("");
        $("#order_total").val("");
        $("#order_payment").val("");
        $("#order_address").val("");
        $("#order_customer_id").val("");
        $("#order_status").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // Check Valid Date
    function isValidDate(date) {
        // Regular expression to check the date format YYYY-MM-DD
        const regex = /^\d{4}-\d{2}-\d{2}$/;
        
        if (!date.match(regex)) return false;
    
        // Construct a Date object from the string and ensure it's valid
        const parts = date.split('-');
        const year = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10);
        const day = parseInt(parts[2], 10);
    
        const dt = new Date(year, month - 1, day);
        
        return dt.getFullYear() === year && dt.getMonth() + 1 === month && dt.getDate() === day;
    }

    // Check Content Empty
    function isContentEmpty(content) {
        return content === "";
    }
    
    // Check Is Number
    function isNumber(value) {
        return !isNaN(parseFloat(value)) && isFinite(value);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#create-btn").click(function () {

        let date = $("#order_date").val();
        let total = $("#order_total").val();
        let payment = $("#order_payment").val();
        let address = $("#order_address").val();
        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        if (!isNumber(total)) {
            flash_message("Invalid total, total should be an integer or decimal");
            return;
        }

        if (isContentEmpty(address)) {
            flash_message("Order Missing Info")
            return;
        }

        let data = {
            "date": date,
            "total": total,
            "payment": payment,
            "address": address,
            "customer_id": customer_id,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message("Order Missing Info")
        });
    });


    // ****************************************
    // Update an Order
    // ****************************************

    $("#update-btn").click(function () {

        let order_id = $("#order_id").val();
        let date = $("#order_date").val();
        let total = $("#order_total").val();
        let payment = $("#order_payment").val();
        let address = $("#order_address").val();
        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        if (!isValidDate(date)) {
            flash_message("Invalid date, date should be valid and in yyyy-mm-dd format");
            return;
        }

        // Check if any field is empty
        if (!order_id || !date || !total || !payment || !address || !customer_id || !status) {
            flash_message("Order Missing Info");
            return;  // Stop the function here
        }

        let data = {
            "date": date,
            "total": total,
            "payment": payment,
            "address": address,
            "customer_id": customer_id,
            "status": status
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            //flash_message(res.responseJSON.message)
            flash_message("Order Not Found")
        });

    });

    // ****************************************
    // Cancel an order
    // ****************************************
    $("#cancel-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message("Cannot cancel non existing order")
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an Order
    // ****************************************

    $("#search-btn").click(function () {
        let order_id = $("#order_id").val();
        let order_date = $("#order_date").val();
        let total = $("#order_total").val();
        let payment = $("#order_payment").val();
        let address = $("#order_address").val();

        $("#flash_message").empty();

        if (order_id || order_date || total || payment || address) {
            flash_message("Only support Customer_id and Status query");
            return;
        }

        let customer_id = $("#order_customer_id").val();
        let status = $("#order_status").val();

        let queryString = ""

        if (customer_id) {
            queryString += 'customer_id=' + customer_id
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Date</th>'
            table += '<th class="col-md-2">Total</th>'
            table += '<th class="col-md-2">Payment</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-2">Customer_id</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for (let i = 0; i < res.length; i++) {
                let order = res[i];
                table += `<tr id="row_${i}"><td>${order.id}</td><td>${order.date}</td><td>${order.total}</td><td>${order.payment}</td><td>${order.address}</td><td>${order.customer_id}</td><td>${order.status}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

})
