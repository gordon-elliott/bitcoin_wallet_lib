# Copyright(c) Gordon Elliott 2014

Feature: Connections can be weighted so transfers are made according to the weight assigned to the connections

  Background: Set up Leveller
    Given we have a leveller
      And a suite of wallets
      | name    | balance | desired | lwm   | hwm   |
      | savings |   600.0 |         |       |       |
      | current |   200.0 |   200.0 | 100.0 | 300.0 |
      | mobile  |    20.0 |    25.0 |  10.0 |  30.0 |
      | online  |    20.0 |    20.0 |   5.0 |  25.0 |
      | tipping |      .2 |      .2 |    .1 |    .3 |
      And the wallets are connected thus
      | source  | destination | weight |
      | savings | current     |      1 |
      | current | mobile      |      1 |
      | current | online      |      1 |
      | mobile  | tipping     |      1 |
      | online  | tipping     |      3 |

  Scenario: Leveller can refill a destination from two source wallets
    When the funds in tipping are adjusted by -0.2 BTC
    Then the leveller will identify that the following transfers are required
    | source  | destination | amount |
    | mobile  | tipping     |   0.05 |
    | online  | tipping     |   0.15 |

  Scenario: Leveller can remove surplus to two source wallets
    When the funds in tipping are adjusted by 0.4 BTC
    Then the leveller will identify that the following transfers are required
    | source | destination | amount |
    | mobile | tipping     |   -0.1 |
    | online | tipping     |   -0.3 |
    And the adjusted balance in the tipping wallet will be 0.2 BTC

  Scenario: Where one of the inputs has insufficient funds they will be drawn from the other inputs
    When the funds in mobile are adjusted by -19.99 BTC
     And the funds in tipping are adjusted by -0.2 BTC
    Then the leveller will identify that the following transfers are required
    | source  | destination | amount |
    | current | mobile      |  24.99 |
    | online  | tipping     |   0.2  |
    And the adjusted balance in the tipping wallet will be 0.2 BTC
