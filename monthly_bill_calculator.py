import csv
from billing_cycle import BillingCycle
from datetime import datetime
# from decimal import Decimal, ROUND_HALF_UP
from itertools import chain
# from tariff_rates import B19Rates

from billing import update_energy_charge_periods, update_demand_charge_periods, finialize_billing_cycle, calculate_monthly_bills
from output import print_monthly_bills, query_bill_details


########################################################

# monthly_bill_calculator.py

# contains main function to run the monthly bill calculator
# as well as functions to read in and parse data from csv file

########################################################


def main():
    run_calculator()


# main function to run the monthly bill calculator
def run_calculator():
    print("Welcome to the Monthly Bill Calculator!")
    print("Please enter the filename of the CSV data to process:")

    # take in filename from user
    filename = input().strip()

    # read in data from csv file and parse into billing cycles
    billing_cycles = read_in_data(filename)

    # calculate and output all billing cycle's bill details
    calculate_monthly_bills(billing_cycles)
    print_monthly_bills(billing_cycles)

    # query loop - while user input is not 'q' continue to ask for month-year to show billing details for that month
    query_bill_details(billing_cycles)


# open and read in data from csv file, then parse data into billing cycles
def read_in_data(filename):
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        # "peak" the first row
        first_row = next(reader)
        start_of_month = int(first_row['Start Date Time'][3:5])
        # prepend iterator back to restart at first entry
        reader = chain([first_row], reader)

        return parse_data(reader, start_of_month)


# parse data into billing cycles
def parse_data(reader, start_of_month):

    billing_cycles = {} # month (int) : BillingCycle - store each billing cycle by month
    billing_days = 0
    days_summer, days_winter = 0, 0
    prev_date = None
    cur_billing_cycle = None
    interval_length = None
    cycles_created = set()
    summer_start = (6, 1)
    summer_end = (9, 30)

    for row in reader:
        start_datetime = row['Start Date Time']
        year = int(start_datetime[6:10])
        month, date, time = int(start_datetime[0:2]), int(start_datetime[3:5]), start_datetime[11:]

        # determine interval length based on first two entries
        if not interval_length and prev_date:
            interval_length = 60 // int((datetime.strptime(start_datetime, "%m-%d-%Y %H:%M") - datetime.strptime(prev_date, "%m-%d-%Y %H:%M")).total_seconds() // 60)

        # Check if we need to start a new billing cycle
        if date == start_of_month and (month, year) not in cycles_created:
            cycles_created.add((month, year)) # make sure we only create one billing cycle per month-year
            if cur_billing_cycle:
                finialize_billing_cycle(cur_billing_cycle, billing_days, days_summer, days_winter, prev_date, interval_length)
                key = (cur_billing_cycle.start_date[0:2] + '-' + cur_billing_cycle.start_date[6:10])
                billing_cycles[key] = cur_billing_cycle

            billing_days = 0
            days_summer, days_winter = 0, 0

            new_billing_cycle = BillingCycle(start_datetime[:10])
            cur_billing_cycle = new_billing_cycle
            cur_billing_cycle.initialize_energy_charge_periods(start_datetime[:5], cur_billing_cycle)
            cur_billing_cycle.initialize_demand_charge_periods(start_datetime[:5], cur_billing_cycle)

        billing_days += 1
        if summer_start <= (month, date) <= summer_end:
            days_summer += 1
        else:
            days_winter += 1

        usage, demand = float(row['Usage'] or 0.0), float(row['Peak Demand'] or 0.0)
        update_energy_charge_periods(cur_billing_cycle, month, date, time, usage)
        update_demand_charge_periods(cur_billing_cycle, month, date, time, demand)

        prev_date = start_datetime

    # finalize last billing cycle
    finialize_billing_cycle(cur_billing_cycle, billing_days, days_summer, days_winter, prev_date, interval_length)
    key = (cur_billing_cycle.start_date[0:2] + '-' + cur_billing_cycle.start_date[6:10])
    billing_cycles[key] = cur_billing_cycle

    return billing_cycles


main()