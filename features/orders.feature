Feature: The order store service back-end
    As an Order Manager
    I need a RESTful catalog service
    So that I can keep track of all my orders

Background:
    Given the following orders
        | date        | total    | payment     | address                                        | customer_id | status      |
        | 2019-05-14  | 871.17   | CREDITCARD  | 59581 Gutierrez Walks North Tyler, NC 31808    | 92931       | OPEN        |
        | 2023-07-16  | 1500.23  | VENMO       | 5th Fifth Ave, NY                              | 3           | SHIPPING    |
        | 2021-01-31  | 200      | DEBITCARD   | Jackson Ave, Queens, NY 11101                  | 1234        | OPEN        |
        | 2020-05-25  | 123.23   | CREDITCARD  | Allen St, New York, NY 10002                   | 768         | DELIVERED   |
        | 2018-08-27  | 779      | VENMO       | 179 E Houston St, New York, NY 10002           | 999         | SHIPPING    |
        
Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Service" in the title
    And I should not see "404 Not Found"


Scenario: List all orders
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "59581 Gutierrez Walks North Tyler, NC 31808" in the results
    And I should see "5th Fifth Ave, NY" in the results
    And I should not see "Jackson Ave, Queens, NY 11101" in the results


