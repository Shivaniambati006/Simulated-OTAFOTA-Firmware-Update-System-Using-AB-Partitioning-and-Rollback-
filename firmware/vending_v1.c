/*
    Firmware V1 - Baseline Vending Machine Program
*/

#include <stdio.h>

int main() {
    printf("[Slot A] Running V1.0 | Standard Pricing Active\n");
    printf("---------------------------------------------\n");

    printf("Menu:\n");
    printf("  1. Soda  - $1.50\n");
    printf("  2. Chips - $1.00\n");
    printf("---------------------------------------------\n");

    int choice;
    printf("Enter item number to buy (1 or 2): ");
    scanf("%d", &choice);

    if (choice == 1) {
        printf("You bought Soda for $1.50 (no discount in V1)\n");
    } else if (choice == 2) {
        printf("You bought Chips for $1.00 (no discount in V1)\n");
    } else {
        printf("Invalid choice.\n");
    }

    printf("---------------------------------------------\n");
    printf("Transaction complete. Firmware V1 finished running.\n");

    return 0;
}