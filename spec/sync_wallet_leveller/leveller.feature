# Copyright(c) Gordon Elliott 2014

Feature: The Leveller manages a set of wallets

  Background: Set up Leveller
    Given we have a leveller

  Scenario Outline: Add an underfunded wallet to the leveller
    Given we have a destination wallet with a balance of <opening balance> BTC
      And we add the destination wallet to the leveller specifying a <low water mark> BTC low water mark and a <high water mark> BTC high water mark
     When we ask the leveller
     Then the leveller can identify that the destination wallet additionally requires <required funds> BTC

    Examples:
    | opening balance | low water mark | high water mark | required funds |
    |            0.0  |            0.0 |             0.0 |           0.0  |
    |            0.0  |            0.1 |             0.1 |           0.1  |
    |            0.0  |            0.1 |             0.2 |           0.2  |
    |            0.1  |            0.1 |             0.2 |           0.0  |
    |            0.2  |            0.1 |             0.2 |           0.0  |
    |            0.05 |            0.1 |             0.2 |           0.15 |
    |            0.07 |            0.1 |             0.2 |           0.13 |
    |        20000.0  |        30000.0 |         40000.0 |       20000.0  |

  Scenario Outline: Add a wallet in surplus to the leveller
    Given we have a destination wallet with a balance of <opening balance> BTC
      And we add the destination wallet to the leveller specifying a <low water mark> BTC low water mark and a <high water mark> BTC high water mark
     When we ask the leveller
     Then the leveller can identify that the destination wallet has <surplus funds> BTC surplus funds

    Examples:
    | opening balance | low water mark | high water mark | surplus funds |
    |            0.0  |            0.0 |             0.0 |          0.0  |
    |            0.1  |            0.1 |             0.2 |          0.0  |
    |            0.2  |            0.1 |             0.2 |          0.0  |
    |            0.3  |            0.1 |             0.2 |         -0.2  |
    |            0.25 |            0.1 |             0.2 |         -0.15 |
    |            0.47 |            0.1 |             0.2 |         -0.37 |
    |        30000.0  |        10000.0 |         20000.0 |     -20000.0  |

#TODO check exception thrown for inconsistent watermarks

#TODO split following scenarios into another feature?

  Scenario: Connect two wallets
    Given we have a source wallet with a balance of 0.1 BTC
      And we have a destination wallet with a balance of 0.1 BTC
      And we add the source wallet to the leveller specifying a 0.1 BTC low water mark and a 0.1 BTC high water mark
      And we add the destination wallet to the leveller specifying a 0.1 BTC low water mark and a 0.1 BTC high water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When the leveller moves 0.004 BTC from the source wallet to the destination wallet
     Then the balance in the source wallet will be 0.096 BTC less the fee
      And the balance in the destination wallet will be 0.104 BTC

  Scenario Outline: Adjust destination wallet
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller specifying a 0.11 BTC low water mark and a 0.9 BTC high water mark
      And we add the destination wallet to the leveller specifying a <destination low water mark> BTC low water mark and a <destination high water mark> BTC high water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that <transfer amount> BTC needs to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | destination low water mark | destination high water mark | transfer amount | comment                                            |
    |                       0.097 |                        0.1 |                         0.2 |           0.103 | partial refill                                     |
    |                       0.0   |                        0.1 |                         0.2 |           0.2   | full refill                                        |
    |                       0.3   |                        0.4 |                         0.5 |           0.2   | another partial within funds available from source |
    |                       0.7   |                        0.4 |                         0.5 |          -0.3   | remove surplus within HWM for source               |
    |                       2.7   |                        0.4 |                         0.5 |          -2.3   | remove surplus greater than HWM for source         |

  Scenario Outline: Adjust destination wallet - no transfer required
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller specifying a 0.11 BTC low water mark and a 0.11 BTC high water mark
      And we add the destination wallet to the leveller specifying a <destination low water mark> BTC low water mark and a <destination high water mark> BTC high water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that no funds need to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | destination low water mark | destination high water mark |
    |                       0.104 |                        0.1 |                         0.2 |
    |                       0.1   |                        0.4 |                         0.4 |
    |                    1000.0   |                        0.4 |                      2000.0 |

  Scenario Outline: Wallet with no low water mark is never automatically refilled
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller specifying a 0.11 BTC low water mark and a 0.9 BTC high water mark
      And we add the destination wallet to the leveller with no low water mark and a <destination high water mark> BTC high water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that no funds need to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | destination high water mark |
    |                         0.0 |                         0.2 |
    |                         0.1 |                         0.2 |
    |                         0.1 |                         0.9 |

  Scenario Outline: Wallet with no high water mark will accept all surplus funds transferred to it
    Given we have a source wallet with a balance of 0.2 BTC
      And we have a destination wallet with a balance of <destination opening balance> BTC
      And we add the source wallet to the leveller with no high water mark and a 0.11 BTC low water mark
      And we add the destination wallet to the leveller specifying a 0.1 BTC low water mark and a 0.2 BTC high water mark
      And we connect the source wallet to the destination wallet specifying a link weight of 1
     When we ask the leveller
     Then the leveller will identify that <transfer amount> BTC needs to be moved from the source wallet to the destination wallet

    Examples:
    | destination opening balance | transfer amount |
    |                        0.0  |             0.2 |
    |                        0.9  |            -0.8 |
    |                    20000.1  |        -20000.0 |
