import math

class LendingProtocol:
    """
    A simplified lending protocol demonstrating core concepts like collateral,
    borrowing, and interest rates. It simulates the logic of a DeFi protocol
    without actual blockchain interaction.
    """
    def __init__(self, name, collateral_factors, borrow_rates):
        self.name = name
        # collateral_factors: dict {asset_symbol: factor_0_to_1}
        # This defines how much a user can borrow against a specific collateral asset.
        self.collateral_factors = collateral_factors
        # borrow_rates: dict {asset_symbol: annual_rate_decimal}
        # This defines the annual interest rate for borrowing a specific asset.
        self.borrow_rates = borrow_rates
        
        # Internal state for deposited collateral and borrowed amounts
        # {user_id: {asset_symbol: amount}}
        self.user_deposits = {}
        self.user_borrows = {}

    def _get_user_data(self, user_id):
        """Helper to ensure user data structures exist."""
        if user_id not in self.user_deposits:
            self.user_deposits[user_id] = {}
        if user_id not in self.user_borrows:
            self.user_borrows[user_id] = {}
        return self.user_deposits[user_id], self.user_borrows[user_id]

    def deposit_collateral(self, user_id, asset, amount):
        """Simulates a user depositing collateral."""
        user_deposits, _ = self._get_user_data(user_id)
        user_deposits[asset] = user_deposits.get(asset, 0) + amount
        print(f"[{self.name}] {user_id} deposited {amount} {asset} as collateral.")

    def get_current_collateral_value(self, user_id, asset_prices):
        """Calculates the total value of a user's deposited collateral."""
        user_deposits, _ = self._get_user_data(user_id)
        total_value = 0
        for asset, amount in user_deposits.items():
            if asset in asset_prices:
                total_value += amount * asset_prices[asset]
        return total_value

    def get_borrowing_power(self, user_id, asset_prices):
        """Calculates the maximum value a user can borrow based on collateral factors."""
        user_deposits, _ = self._get_user_data(user_id)
        borrowing_power = 0
        for asset, amount in user_deposits.items():
            if asset in asset_prices and asset in self.collateral_factors:
                # Borrowing power is calculated by applying the collateral factor
                # to the value of each deposited asset.
                borrowing_power += amount * asset_prices[asset] * self.collateral_factors[asset]
        return borrowing_power

    def get_current_borrowed_value(self, user_id, asset_prices):
        """Calculates the total value of a user's current outstanding borrows."""
        _, user_borrows = self._get_user_data(user_id)
        total_borrowed_value = 0
        for asset, amount in user_borrows.items():
            if asset in asset_prices:
                total_borrowed_value += amount * asset_prices[asset]
        return total_borrowed_value

    def borrow(self, user_id, borrow_asset, amount, asset_prices):
        """Simulates a user borrowing an asset."""
        user_deposits, user_borrows = self._get_user_data(user_id)

        if borrow_asset not in self.borrow_rates:
            print(f"[{self.name}] Error: {borrow_asset} is not an available asset to borrow.")
            return False

        current_borrowed_value = self.get_current_borrowed_value(user_id, asset_prices)
        potential_new_borrow_value = amount * asset_prices.get(borrow_asset, 0)
        
        # Check if the user has enough borrowing power according to the protocol's rules
        max_borrow_value = self.get_borrowing_power(user_id, asset_prices)
        
        if (current_borrowed_value + potential_new_borrow_value) > max_borrow_value:
            print(f"[{self.name}] Error: {user_id} cannot borrow {amount} {borrow_asset}.")
            print(f"  Current borrowed value: ${current_borrowed_value:.2f}")
            print(f"  Max borrowing power:    ${max_borrow_value:.2f}")
            return False
        
        user_borrows[borrow_asset] = user_borrows.get(borrow_asset, 0) + amount
        print(f"[{self.name}] {user_id} successfully borrowed {amount} {borrow_asset}.")
        return True

    def calculate_annual_interest(self, user_id, asset):
        """Calculates the annual interest for a specific borrowed asset."""
        _, user_borrows = self._get_user_data(user_id)
        borrowed_amount = user_borrows.get(asset, 0)
        if borrowed_amount > 0 and asset in self.borrow_rates:
            # Annual interest is simply the borrowed amount multiplied by the annual rate.
            return borrowed_amount * self.borrow_rates[asset]
        return 0

# --- Simulation Setup ---
# Define current asset prices (e.g., from an oracle feed)
ASSET_PRICES = {
    "ETH": 2000,  # 1 ETH = $2000
    "USDC": 1,    # 1 USDC = $1
}

# --- Compound V2-like Parameters ---
# V2 is simulated with more permissive ETH collateral and a lower USDC borrow rate.
V2_COLLATERAL_FACTORS = {
    "ETH": 0.8,  # Can borrow up to 80% of ETH value
    "USDC": 0.9,
}
V2_BORROW_RATES = {
    "USDC": 0.05, # 5% annual interest rate for USDC
    "ETH": 0.03,
}
compound_v2 = LendingProtocol("Compound V2", V2_COLLATERAL_FACTORS, V2_BORROW_RATES)

# --- Compound V3-like Parameters ---
# V3 is simulated with more conservative ETH collateral and a higher USDC borrow rate.
# These changes represent common types of updates in protocol upgrades.
V3_COLLATERAL_FACTORS = {
    "ETH": 0.7,  # Reduced from V2: Can borrow up to 70% of ETH value
    "USDC": 0.85,
}
V3_BORROW_RATES = {
    "USDC": 0.07, # Increased from V2: 7% annual interest rate for USDC
    "ETH": 0.04,
}
compound_v3 = LendingProtocol("Compound V3", V3_COLLATERAL_FACTORS, V3_BORROW_RATES)

print("--- Scenario: User interacts with Compound V2 ---")
user_a = "UserA"
initial_eth_deposit = 10 # ETH
usdc_to_borrow_v2 = 1000 # USDC

# User deposits collateral in V2
compound_v2.deposit_collateral(user_a, "ETH", initial_eth_deposit)

# Calculate borrowing power in V2 based on V2's collateral factors
v2_borrowing_power = compound_v2.get_borrowing_power(user_a, ASSET_PRICES)
print(f"[{compound_v2.name}] {user_a}'s borrowing power with {initial_eth_deposit} ETH: ${v2_borrowing_power:.2f}")

# User attempts to borrow USDC in V2
print(f"[{compound_v2.name}] {user_a} attempts to borrow {usdc_to_borrow_v2} USDC.")
compound_v2.borrow(user_a, "USDC", usdc_to_borrow_v2, ASSET_PRICES)

# Calculate V2 interest based on V2's borrow rates
v2_annual_interest = compound_v2.calculate_annual_interest(user_a, "USDC")
print(f"[{compound_v2.name}] {user_a}'s annual interest for USDC borrow: ${v2_annual_interest:.2f}\n")

print("--- Compatibility Review: What if this position were on Compound V3? ---")
print("This section simulates how V3's *new rules* would impact an existing V2 position or new actions.")

# Re-evaluate UserA's position *as if* it were on V3
# This demonstrates the 'compatibility review' aspect: how an existing state
# fares under new protocol rules.
print(f"[{compound_v3.name}] Evaluating {user_a}'s position with V3 rules (same collateral, same borrowed amount):")

# V3's borrowing power for the same collateral, but with V3's (stricter) collateral factors
v3_borrowing_power = compound_v3.get_borrowing_power(user_a, ASSET_PRICES)
print(f"  {user_a}'s borrowing power with {initial_eth_deposit} ETH under V3 rules: ${v3_borrowing_power:.2f}")

# Check if the V2 borrow amount is still valid under V3 rules
v2_borrowed_value = usdc_to_borrow_v2 * ASSET_PRICES["USDC"]
if v2_borrowed_value > v3_borrowing_power:
    # This highlights a potential liquidation risk or inability to borrow more
    print(f"  WARNING: {user_a}'s existing borrow of ${v2_borrowed_value:.2f} would exceed V3's borrowing power!")
    print(f"  This indicates a potential liquidation risk or a need to repay/add collateral under V3.")
else:
    print(f"  {user_a}'s existing borrow of ${v2_borrowed_value:.2f} is still within V3's borrowing power.")

# Calculate V3 interest for the same borrowed amount, but with V3's (higher) borrow rates
v3_annual_interest = usdc_to_borrow_v2 * V3_BORROW_RATES["USDC"]
print(f"  {user_a}'s annual interest for the same USDC borrow under V3 rules: ${v3_annual_interest:.2f}")
print(f"  (V2 interest was ${v2_annual_interest:.2f}. V3 is higher due to rate increase.)\n")

print("--- Scenario: New borrow attempt under Compound V3 rules ---")
user_b = "UserB"
initial_eth_deposit_b = 10 # ETH
usdc_to_borrow_v3 = 1000 # USDC

compound_v3.deposit_collateral(user_b, "ETH", initial_eth_deposit_b)
v3_borrowing_power_b = compound_v3.get_borrowing_power(user_b, ASSET_PRICES)
print(f"[{compound_v3.name}] {user_b}'s borrowing power with {initial_eth_deposit_b} ETH: ${v3_borrowing_power_b:.2f}")

print(f"[{compound_v3.name}] {user_b} attempts to borrow {usdc_to_borrow_v3} USDC.")
compound_v3.borrow(user_b, "USDC", usdc_to_borrow_v3, ASSET_PRICES)

v3_annual_interest_b = compound_v3.calculate_annual_interest(user_b, "USDC")
print(f"[{compound_v3.name}] {user_b}'s annual interest for USDC borrow: ${v3_annual_interest_b:.2f}")

# Demonstrate a failed borrow due to V3's stricter rules
print("\n--- Scenario: User B tries to borrow more than V3 allows ---")
usdc_excess_borrow_v3 = 1500 # More than what 10 ETH collateral (0.7 factor) allows
print(f"[{compound_v3.name}] {user_b} attempts to borrow an additional {usdc_excess_borrow_v3} USDC.")
compound_v3.borrow(user_b, "USDC", usdc_excess_borrow_v3, ASSET_PRICES)
