# Copyright(c) Gordon Elliott 2014

Feature: The Leveller can spot nodes with inconsistent thresholds

  Background: Set up Leveller
    Given we have a leveller

  Scenario: Water marks are correct
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 200, 100 and 300 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is no conflict between the watermarks

  Scenario: Water marks are correct but identical
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 200, 200 and 200 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is no conflict between the watermarks

  Scenario: High water mark too low
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 200, 100 and 30 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is a conflict between the watermarks

  Scenario: Low water mark too high
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 200, 1000 and 300 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is a conflict between the watermarks

  Scenario: Desired level too low
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 20, 100 and 300 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is a conflict between the watermarks

  Scenario: Desired level too high
    Given we have a test wallet with a balance of 200 BTC
      And we add the test wallet to the leveller specifying 2000, 100 and 300 BTC desired level, low water mark and high water mark
     When we ask the leveller
     Then the leveller can spot that there is a conflict between the watermarks

