Feature: The Leveller manages a set of wallets

  Background: Set up Leveller
    Given we have a leveller

  Scenario Outline: Add a wallet to the leveller
    Given we have a destination wallet with a balance of <opening balance> BTC
      And we add the destination wallet to the leveller specifying a <low water mark> BTC low water mark
     When we ask the leveller
     Then the leveller can identify that the destination wallet additionally requires <required funds> BTC

    Examples:
    | opening balance | low water mark | required funds |
    |             0.0 |            0.0 |            0.0 |
    |             0.0 |            0.1 |            0.1 |
    |             0.1 |            0.1 |            0.0 |
    |             0.2 |            0.1 |            0.0 |
    |            0.05 |            0.1 |           0.05 |
    |            0.07 |            0.1 |           0.03 |
    |         20000.0 |        30000.0 |        10000.0 |

  Scenario: Connect two wallets
    Given we have a source wallet with a balance of 0.1 BTC
      And we have a destination wallet with a balance of 0.1 BTC
      And we add the source wallet to the leveller specifying a 0.1 BTC low water mark
      And we add the destination wallet to the leveller specifying a 0.1 BTC low water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When the leveller moves 0.004 BTC from the source wallet to the destination wallet
     Then the balance in the source wallet will be 0.096 BTC less the fee
      And the balance in the destination wallet will be 0.104 BTC

  Scenario Outline: Refill destination wallet
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller specifying a 0.11 BTC low water mark
      And we add the destination wallet to the leveller specifying a <destination low water mark> BTC low water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that <transfer amount> BTC needs to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | destination low water mark | transfer amount |
    |                       0.097 |                        0.1 |           0.003 |
    |                       0.0   |                        0.1 |           0.1   |
    |                       0.3   |                        0.4 |           0.1   |

  Scenario Outline: Refill destination wallet - no transfer required
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller specifying a 0.11 BTC low water mark
      And we add the destination wallet to the leveller specifying a <destination low water mark> BTC low water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that no funds need to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | destination low water mark |
    |                       0.104 |                        0.1 |
    |                       0.1   |                        0.4 |
    |                    1000.0   |                        0.4 |
