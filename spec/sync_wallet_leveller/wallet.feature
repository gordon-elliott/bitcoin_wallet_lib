# Copyright(c) Gordon Elliott 2014

Feature: Wallets manage funds

  Scenario: Transfer 0.004 BTC between wallets
    Given we have a source wallet with a balance of 0.1 BTC
      And we have a destination wallet with a balance of 0.1 BTC
     When we transfer 0.004 BTC from source to destination
     Then the balance in the source wallet will be 0.096 BTC less the fee
      And the balance in the destination wallet will be 0.104 BTC

  Scenario: Trying to spend more than the balance in a wallet is not allowed
    Given we have a source wallet with a balance of 0.001 BTC
      And we have a destination wallet with a balance of 0.1 BTC
     When we transfer 0.004 BTC from source to destination
     Then the balance in the source wallet will be 0.001 BTC
      And the balance in the destination wallet will be 0.1 BTC

