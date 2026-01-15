from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from tariff_rates import B19Rates

########################################################

# output.py

# contains function definitions to display monthly bill
# summaries and breakdowns for user

########################################################


period_display = {
    'max_peak': 'Max Peak Demand',
    'max_part_peak': 'Max Part-Peak Demand',
    'max_demand': 'Max Demand',
    'peak': 'Peak Energy Usage',
    'part_peak': 'Part-Peak Energy Usage',
    'off_peak': 'Off-Peak Energy Usage',
    'super_off_peak': 'Super Off-Peak Energy Usage'
}

# print summary of monthly bills for all billing cycles
def print_monthly_bills(billing_cycles):

    print('\n', "* * * * * Monthly Bill Details * * * * * ", '\n')

    INDENT = " " * 2

    for cycle in billing_cycles:
        cur_cycle = billing_cycles[cycle]
        print(f"Bill for: {cur_cycle.start_date} to {cur_cycle.end_date} ({cur_cycle.billing_days} billing day(s))")

        print(f"{INDENT}Customer Charge: ${cur_cycle.customer_charge:,.2f}")
        print(f"{INDENT}Demand Charge: ${cur_cycle.demand_charge:,.2f}")
        print(f"{INDENT}Energy Charge: ${cur_cycle.energy_charge:,.2f}")

        line = '  ' + ('-' * (15 + len(str(cur_cycle.total_charge))))
        print(line)
        print(f"{INDENT}Total Charge: ${cur_cycle.energy_charge:,.2f}", '\n')


# print detailed bill information for a specific billing cycle
def print_bill_details(billing_cycles, user_input):
    print('\n', "* * * * * Detailed Bill Information * * * * *", '\n')

    INDENT = " " * 2

    cur_cycle = billing_cycles[user_input]
    print(f"{INDENT}Start Date: {cur_cycle.start_date}")
    print(f"{INDENT}End Date: {cur_cycle.end_date}")
    print(f"{INDENT}Billing Days: {cur_cycle.billing_days} days (Summer Days: {cur_cycle.days_in_season['summer']}, Winter Days: {cur_cycle.days_in_season['winter']})")

    month = int(cur_cycle.start_date[0:2])
    day = int(cur_cycle.start_date[3:5])

    summer_start = (6, 1)
    summer_end = (9, 30)

    print('\n', " Billing Breakdown:", '\n')
    if summer_start <= (month, day) <= summer_end:
        display_summer_rates(cur_cycle)
        if (9, 2) <= (month, day) <= (9, 30):
            display_winter_rates(cur_cycle)
    else:
        display_winter_rates(cur_cycle)
        if (5, 2) <= (month, day) <= (5, 31):
            display_summer_rates(cur_cycle)

    line = '  ' + ('-' * (15 + len(str(cur_cycle.total_charge))))
    print(line)
    print(f"{INDENT}Total Charge: ${cur_cycle.energy_charge:,.2f}", '\n')


# display winter rate details
def display_winter_rates(cur_cycle):
    print("  Winter Rates")

    INDENT = " " * 4

    # print customer charge details
    print("  > Customer Charge:")
    days = cur_cycle.days_in_season['winter']
    rate = B19Rates['customer_charge_rates']['mandatory']
    customer_charge_winter = Decimal(cur_cycle.customer_charge / cur_cycle.billing_days * cur_cycle.days_in_season['winter'])
    amount = customer_charge_winter.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print(f"{INDENT}{days} days @ ${rate:.5f} per day -> ${amount:,.2f}")

    # print demand charge details
    print("  > Demand Charge:")
    for period in cur_cycle.demand_charge_periods['winter']:
        value = cur_cycle.demand_charge_periods['winter'][period].value
        rate = B19Rates['demand_charge_rates']['winter'][period]
        demand_amount = cur_cycle.demand_charge_periods['winter'][period].cost
        print(f"{INDENT}{period_display[period]}: {value:,.6f} kW @ ${rate:,.5f} per kW for {days} winter days / {cur_cycle.billing_days} billing days -> ${demand_amount:,.2f}")

    # print energy charge details
    print("  > Energy Charge:")
    for period in cur_cycle.energy_charge_periods['winter']:
        value = cur_cycle.energy_charge_periods['winter'][period].value
        rate = B19Rates['energy_charge_rates']['winter'][period]
        energy_amount = cur_cycle.energy_charge_periods['winter'][period].cost
        print(f"{INDENT}{period_display[period]}: {value:,.6f} kWh @ ${rate:,.5f} per kWh -> ${energy_amount:,.2f}")


# display summer rate details
def display_summer_rates(cur_cycle):
    print("  Summer Rates")

    INDENT = " " * 4

    # print customer charge details
    print("  > Customer Charge:")
    days = cur_cycle.days_in_season['summer']
    rate = B19Rates['customer_charge_rates']['mandatory']
    customer_charge_summer = Decimal(cur_cycle.customer_charge / cur_cycle.billing_days * cur_cycle.days_in_season['summer'])
    amount = customer_charge_summer.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    print(f"{INDENT}{days} days @ ${rate:.5f} per day -> ${amount:,.2f}")

    # print demand charge details
    print("  > Demand Charge:")
    for period in cur_cycle.demand_charge_periods['summer']:
        value = cur_cycle.demand_charge_periods['summer'][period].value
        rate = B19Rates['demand_charge_rates']['summer'][period]
        demand_amount = cur_cycle.demand_charge_periods['summer'][period].cost
        print(f"{INDENT}{period_display[period]}: {value:,.6f} kW @ ${rate:,.5f} per kW for {days} summer days / {cur_cycle.billing_days} billing days -> ${demand_amount:,.2f}")

    # print energy charge details
    print("  > Energy Charge:")
    for period in cur_cycle.energy_charge_periods['summer']:
        value = cur_cycle.energy_charge_periods['summer'][period].value
        rate = B19Rates['energy_charge_rates']['summer'][period]
        energy_amount = cur_cycle.energy_charge_periods['summer'][period].cost
        print(f"{INDENT}{period_display[period]}: {value:,.6f} kWh @ ${rate:,.5f} per kWh -> ${energy_amount:,.2f}")


# query billing details for specific month-year or quit
def query_bill_details(billing_cycles):

    def is_valid_mm_yyyy(value: str) -> bool:
        try:
            datetime.strptime(value, "%m-%Y")
            return True
        except ValueError:
            return False

    # query loop - while user input is not 'q' continue to ask for month-year to show billing details for that month
    print("Would you like to see detailed billing information? (enter month and year in the format 'mm-yyyy' for a specific month, or 'q' to quit)")

    user_input = input().strip()
    while user_input != 'q':

        if not is_valid_mm_yyyy(user_input):
            print("Invalid input. Please enter month and year in the format 'mm-yyyy', or 'q' to quit.")
            user_input = input().strip()
            continue

        if user_input not in billing_cycles:
            print("No billing cycle found for that month and year. Please try again.")
            user_input = input().strip()
            continue

        print_bill_details(billing_cycles, user_input)

        print('\n', "Would you like to see more detailed billing information? (enter month and year in the format 'mm-yyyy' for a specific month, or 'q' to quit)")
        user_input = input().strip()

    print("Thank you for using the Monthly Bill Calculator! Have a great day!")
