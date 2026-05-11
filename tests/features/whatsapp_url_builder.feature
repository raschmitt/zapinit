Feature: WhatsApp URL builder

  Scenario Outline: Build wa.me URL from E.164 number
    Given the E.164 number is "<e164>"
    When the URL is built
    Then the result is "<expected_url>"

    Examples:
      | e164             | expected_url                        |
      | +5511999999999   | https://wa.me/5511999999999         |
      | +14155550100     | https://wa.me/14155550100           |
      | +447911123456    | https://wa.me/447911123456          |
      | 5511999999999    | https://wa.me/5511999999999         |
      | +55 11 99999 9999 | https://wa.me/5511999999999         |
      | +55-11-99999-9999 | https://wa.me/5511999999999         |
