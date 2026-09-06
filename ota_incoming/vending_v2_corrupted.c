/*
    Firmware V2 - Upgraded Vending Machine Program
    ------------------------------------------------
    New in this version:
    - Loyalty Discount: buying the same item twice
      in one session gives a 10% discount on the
      second purchase.
*/

#include <stdio.h>

int main() {
    printf("[Slot B] Running V2.0 | Loyalty Discount Feature Active\n");
    printf("---------------------------------------------\n");

    printf("Menu:\n");
    printf("  1. Soda  - $1.50\n");
    printf("  2. Chips - $1.00\n");
    printf("---------------------------------------------\n");

    int firstChoice, secondChoice;
    float price = 0.0;

    // First purchase
    printf("Enter item number to buy (1 or 2): ");
    scanf("%d", &firstChoice);

    if (firstChoice == 1) {
        printf("You bought Soda for $1.50\n");
    } else if (firstChoice == 2) {
        printf("You bought Chips for $1.00\n");
    } else {
        printf("Invalid choice.\n");
        return 1;
    }

    // Ask if they want to buy again (to trigger loyalty discount)
    printf("---------------------------------------------\n");
    printf("Buy another item to test the Loyalty Discount? (1 = Soda, 2 = Chips, 0 = No): ");
    scanf("%d", &secondChoice);

    if (secondChoice == firstChoice && secondChoice != 0) {
        price = (secondChoice == 1) ? 1.50 : 1.00;
        float discounted = price * 0.90; // 10% off
        printf("Loyalty Discount applied! Second item price: $%.2f (was $%.2f)\n", discounted, price);
    } else if (secondChoice == 0) {
        printf("No second purchase made.\n");
    } else {
        printf("Different item chosen - no loyalty discount this time.\n");
    }

    printf("---------------------------------------------\n");
    printf("Transaction complete. Firmware V2 finished running.\n");

    return 0;
}// corrupted junk data cp firmware/vending_v2_valid.c ota_incoming/vending_v2_corrupted.c! @@@ ###
