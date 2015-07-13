# Copyright(c) Gordon Elliott 2014

Feature: The Leveller may not have root nodes with a high water mark

  Scenario: Leveller can identify a single root node with a high water mark
    Given we have a leveller
      And a suite of wallets
      | name    | balance | desired | lwm   | hwm   |
      | savings |   600.0 |         |       | 999.9 |
      | current |   200.0 |   200.0 | 100.0 | 300.0 |
      And the wallets are connected thus
      | source  | destination | weight |
      | savings | current     |      1 |
    When the wallets are added to the leveller
    Then the leveller can spot that the defined network has root nodes with a high water mark

  Scenario: Leveller can identify a multiple root nodes with a high water mark
    Given we have a leveller
      And a suite of wallets
      | name    | balance | desired | lwm   | hwm   |
      | mobile  |    20.0 |    25.0 |  10.0 |  30.0 |
      | online  |    20.0 |    20.0 |   5.0 |  25.0 |
      | tipping |      .2 |      .2 |    .1 |    .3 |
      And the wallets are connected thus
      | source  | destination | weight |
      | mobile  | tipping     |      1 |
      | online  | tipping     |      1 |
    When the wallets are added to the leveller
    Then the leveller can spot that the defined network has root nodes with a high water mark
