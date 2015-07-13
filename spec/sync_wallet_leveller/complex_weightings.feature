# Copyright(c) Gordon Elliott 2014

Feature: Complex transfer rules can be implemented using the weightings

  Background: Set up Leveller
    Given we have a leveller
      And a suite of wallets
      | name      | balance | desired | lwm    | hwm    |
      | grandma   |  6000.0 |  6000.0 | 5000.0 |        |
      | grandpa   |    10.0 |    10.0 |    7.0 |   80.0 |
      | mum       |  2000.0 |  2000.0 | 1950.0 | 2050.0 |
      | dad       |  2000.0 |  2000.0 | 1950.0 | 2050.0 |
      | millie    |   200.0 |   200.0 |  100.0 |  300.0 |
      | chad      |   200.0 |   200.0 |  100.0 |  300.0 |
      And the wallets are connected thus
      | source  | destination | weight |
      | grandma | grandpa     |      2 |
      | grandma | mum         |     99 |
      | grandma | dad         |     99 |
      | grandpa | millie      |      2 |
      | mum     | millie      |     99 |
      | dad     | millie      |     99 |
      | grandpa | chad        |      2 |
      | mum     | chad        |     99 |
      | dad     | chad        |     99 |

  Scenario: Leveller can percolate funds up through the network
    When the funds in millie are adjusted by 1000 BTC
    Then the leveller can check that the defined network is valid
    And the leveller will identify that the following transfers are required
    | source    | destination | amount |
    | grandpa   | millie      |    -10 |
    | mum       | millie      |   -495 |
    | dad       | millie      |   -495 |
    | grandma   | mum         |   -495 |
    | grandma   | dad         |   -495 |

  Scenario: Leveller can percolate funds down through the network
    When the funds in millie are adjusted by -200 BTC
     And the funds in chad are adjusted by -200 BTC
    Then the leveller can check that the defined network is valid
    And the leveller will identify that the following transfers are required
    | source    | destination |  amount |
    | grandma   | grandpa     |       4 |
    | grandma   | mum         |     198 |
    | grandma   | dad         |     198 |
    | grandpa   | millie      |       2 |
    | grandpa   | chad        |       2 |
    | mum       | millie      |      99 |
    | mum       | chad        |      99 |
    | dad       | millie      |      99 |
    | dad       | chad        |      99 |
