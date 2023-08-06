Feature: The order store service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keep track of all my orders

    Background:
        Given the following orders
            | date       | total   | payment    | address                                     | customer_id | status    |
            | 2019-05-14 | 871.17  | CREDITCARD | 59581 Gutierrez Walks North Tyler, NC 31808 | 92931       | OPEN      |
            | 2023-07-16 | 1500.23 | VEMO       | 5th Fifth Ave, NY                           | 3           | SHIPPING  |
            | 2021-01-31 | 200     | DEBITCARD  | Jackson Ave, Queens, NY 11101               | 1234        | OPEN      |
            | 2020-05-25 | 123.23  | CREDITCARD | Allen St, New York, NY 10002                | 768         | DELIVERED |
            | 2019-01-01 | 100     | CREDITCARD | 5th Fifth Ave, NY                           | 11          | OPEN      |
            | 2020-01-01 | 200     | CREDITCARD | 6th Fifth Ave, NY                           | 22          | SHIPPING  |
            | 2021-01-01 | 300     | DEBITCARD  | 7th Fifth Ave, NY                           | 33          | DELIVERED |
            | 2022-01-01 | 400     | VEMO       | 8th Fifth Ave, NY                           | 44          | CANCELLED |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Order Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create an Order
        When I visit the "Home Page"
        And I set the "Date" to "2019-05-14"
        And I set the "Total" to "871.17"
        And I select "CREDITCARD" in the "Payment" dropdown
        And I set the "Address" to "59581 Gutierrez Walks North Tyler, NC 31808"
        And I set the "Customer_id" to "92931"
        And I select "OPEN" in the "Status" dropdown
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Date" field should be empty
        And the "Total" field should be empty
        And the "Address" field should be empty
        And the "Customer_id" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "2019-05-14" in the "Date" field
        And I should see "871.17" in the "Total" field
        And I should see "CREDITCARD" in the "Payment" dropdown
        And I should see "59581 Gutierrez Walks North Tyler, NC 31808" in the "Address" field
        And I should see "92931" in the "Customer_id" field
        And I should see "OPEN" in the "Status" dropdown

    Scenario: Search by customer id
        When I visit the "Home Page"
        And I set the "Customer ID" to "11"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "11" in the results
        And I should not see "6th Fifth Ave, NY" in the results
        And I should not see "7th Fifth Ave, NY" in the results
        And I should not see "8th Fifth Ave, NY" in the results

    Scenario: Search by status
        When I visit the "Home Page"
        And I select "OPEN" in the "Status" dropdown
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "OPEN" in the results
        And I should not see "SHIPPING" in the results
        And I should not see "DELIVERED" in the results
        And I should not see "CANCELLED" in the results

    Scenario: Search by status and customer id
        When I visit the "Home Page"
        And I select "OPEN" in the "Status" dropdown
        And I set the "Customer ID" to "11"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "OPEN" in the results
        And I should not see "SHIPPING" in the results
        And I should not see "DELIVERED" in the results
        And I should not see "CANCELLED" in the results
        And I should see "11" in the results
        And I should not see "6th Fifth Ave, NY" in the results
        And I should not see "7th Fifth Ave, NY" in the results
        And I should not see "8th Fifth Ave, NY" in the results

    Scenario: List all orders
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "59581 Gutierrez Walks North Tyler, NC 31808" in the results
        And I should see "5th Fifth Ave, NY" in the results
        And I should see "Jackson Ave, Queens, NY 11101" in the results
        And I should not see "CASH" in the results

    Scenario: Read an order
        When I visit the "Home Page"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Date" field should be empty
        And the "Address" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "2019-05-14" in the "date" field
        And I should see "871.17" in the "total" field
        And I should see "CREDITCARD" in the "payment" dropdown
        And I should see "59581 Gutierrez Walks North Tyler, NC 31808" in the "address" field
        And I should see "92931" in the "customer_id" field
        And I should see "OPEN" in the "status" dropdown

    Scenario: Delete an Order
        When I visit the "Home Page"
        And I set the "Customer ID" to "11"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "11" in the results
        When I copy the "Id" field
        And I press the "Clear" button
        Then the "Id" field should be empty
        And the "Date" field should be empty
        And the "Address" field should be empty
        When I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "2019-01-01" in the "date" field
        And I should see "100" in the "total" field
        And I should see "CREDITCARD" in the "payment" dropdown
        And I should see "5th Fifth Ave, NY" in the "address" field
        When I press the "Delete" button
        Then I should see the message "Order has been Deleted!"

    Scenario: Cancel an Order
        When I visit the "Home Page"
        And I set the "Customer ID" to "11"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "11" in the results
        When I copy the "Id" field
        And I press the "Cancel" button
        Then I should see the message "Success"
        And I should see "CANCELLED" in the "Status" dropdown

    Scenario: Update an Order
        When I visit the "Home Page"
        And I set the "Customer_id" to "92931"
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "92931" in the "Customer_id" field
        And I should see "59581 Gutierrez Walks North Tyler, NC 31808" in the "Address" field
        When I change "Customer_id" to "13929"
        And I press the "Update" button
        Then I should see the message "Success"
        When I copy the "Id" field
        And I press the "Clear" button
        And I paste the "Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "13929" in the "Customer_id" field
        When I press the "Clear" button
        And I press the "Search" button
        Then I should see the message "Success"
        And I should see "13929" in the results
        And I should not see "92931" in the results
