#!/usr/bin/env python
"""Cardano Pool Checker main module."""

from cardano_pool_checker.cardano_pool_checker_class import CardanoPoolChecker


def main():
    """Run the main entry point of the program.

    This function is responsible for initializing the application,
    processing command-line arguments, and orchestrating the program's
    execution.

    Returns:
        None: This function doesn't return any values.
    """
    my_checker = CardanoPoolChecker()
    my_checker.update()


if __name__ == "__main__":
    main()
