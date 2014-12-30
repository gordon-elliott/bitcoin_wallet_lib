# Copyright(c) Gordon Elliott 2014

# TODO implement .feature for weightings
# TODO root minimize, leaf maximise, intermediate midpoint
# TODO multi root scenario

Feature: The Leveller identifies the transfers needed to bring the suite of wallets into balance

  Background: Set up Leveller
    Given we have a leveller
      And a suite of wallets
      | name    | balance | lwm   | hwm   |
      | savings |   600.0 |       |       |
      | current |   200.0 | 100.0 | 300.0 |
      | mobile  |    20.0 |  10.0 |  30.0 |
      | online  |    20.0 |   5.0 |  25.0 |
      | tipping |      .2 |    .1 |    .3 |
      And the wallets are connected thus
      | source  | destination | weight |
      | savings | current     | 1.0    |
      | current | mobile      | 1.0    |
      | current | online      | 1.0    |
      | mobile  | tipping     | 1.0    |
      | online  | tipping     | 1.0    |

  Scenario Outline: Leveller can identify simple, single transfers
    When the funds in <modified wallet> are adjusted by <payment amount> BTC
    Then the leveller will identify that <balancing amount> BTC needs to be moved from the <source> wallet to the <destination> wallet

    Examples:
    | modified wallet | payment amount | balancing amount | source  | destination |
    | current         |         -150.0 |            250.0 | savings | current     |
    | current         |          200.0 |           -300.0 | savings | current     |
    | mobile          |          -15.0 |             25.0 | current | mobile      |
    | mobile          |           20.0 |            -30.0 | current | mobile      |
    | online          |          -20.0 |             25.0 | current | online      |
    | online          |           80.0 |            -95.0 | current | online      |

  Scenario: Leveller may cause cascading transfers
    When the funds in mobile are adjusted by -18 BTC
     And the funds in current are adjusted by -90 BTC
    Then the leveller will identify that the following transfers are required
    | source  | destination | amount |
    | current | mobile      |   28.0 |
    | savings | current     |  218.0 |