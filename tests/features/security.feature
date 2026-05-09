Feature: Security controls

  Scenario: WhatsApp tab opens without opener access
    Given the app JavaScript is loaded
    Then the WhatsApp redirect uses "noopener,noreferrer" to prevent tabnabbing
