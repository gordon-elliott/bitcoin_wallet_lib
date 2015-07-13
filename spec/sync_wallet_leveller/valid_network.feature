# Copyright(c) Gordon Elliott 2014

Feature: The Leveller connects the wallets into a directed, acyclic graph (DAG)

  Background: Set up Leveller
    Given we have a leveller
      And a suite of wallets
      | name    | balance | desired | lwm   | hwm   |
      | savings |   600.0 |         |       |       |
      | current |   200.0 |   200.0 | 100.0 | 300.0 |
      | mobile  |    20.0 |    25.0 |  10.0 |  30.0 |
      | online  |    20.0 |    20.0 |   5.0 |  25.0 |
      | tipping |      .2 |      .2 |    .1 |    .3 |

  Scenario: Leveller can load a correctly formed graph of wallets
    Given the wallets are connected thus
    | source  | destination | weight |
    | savings | current     |      1 |
    | current | mobile      |      1 |
    | current | online      |      1 |
    | mobile  | tipping     |      1 |
    | online  | tipping     |      1 |
    When the wallets are added to the leveller
    Then the leveller can check that the defined network is valid
     And the leveller finds no funds need to be moved

  Scenario: Leveller can identify an incorrectly formed graph of wallets
    Given the wallets are connected thus
    | source  | destination | weight |
    | savings | current     |      1 |
    | current | mobile      |      1 |
    | current | online      |      1 |
    | mobile  | tipping     |      1 |
    | online  | current     |      1 |
    When the wallets are added to the leveller
    Then the leveller can spot that the defined network includes cycles

  Scenario: Leveller can identify duplicate connections between wallets
    Given the wallets are connected thus:
    | source  | destination | weight |
    | savings | current     |      1 |
    | current | mobile      |      1 |
    | current | mobile      |      1 |
    When the wallets are added to the leveller
    Then the leveller can spot that a duplicate connection between wallets has been specified
    
