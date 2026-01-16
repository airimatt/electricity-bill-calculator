import csv
from billing_cycle import BillingCycle
from datetime import datetime
from itertools import chain

from billing import update_energy_charge_periods, update_demand_charge_periods, finialize_billing_cycle


########################################################

# preprocess.py

# contains function definitions to read in and process
# data from csv file into billing cycle objects

########################################################


# prompts user for a valid csv and checks for errors
def open_valid_file():
    while True:
        filename = input("Enter CSV filename: ")
        try:
            with open(filename, newline='') as file:
                reader = csv.DictReader(file)

                # Ensure header row exists
                if reader.fieldnames is None:
                    raise ValueError("Missing header row")

                # Ensure csv is not empty
                try:
                    next(reader)
                except StopIteration:
                    raise ValueError("CSV is empty")

            # success - return filename
            return filename

        except FileNotFoundError:
            print("File not found. Please try again.")
        except PermissionError:
            print("Permission denied. Please try again.")
        except (csv.Error, ValueError) as e:
            print(f"Invalid CSV: {e}. Please try again.")


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
    summer_start, summer_end = (6, 1), (9, 30)

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
            cur_billing_cycle.initialize_energy_charge_periods(cur_billing_cycle)
            cur_billing_cycle.initialize_demand_charge_periods(cur_billing_cycle)

        # increment billing days and seasonal days (will offset later based on interval length)
        billing_days += 1
        if summer_start <= (month, date) <= summer_end:
            days_summer += 1
        else:
            days_winter += 1

        # update the energy and demand charge values
        usage, demand = float(row['Usage'] or 0.0), float(row['Peak Demand'] or 0.0)
        update_energy_charge_periods(cur_billing_cycle, month, date, time, usage)
        update_demand_charge_periods(cur_billing_cycle, month, date, time, demand)

        prev_date = start_datetime

    # finalize last billing cycle
    finialize_billing_cycle(cur_billing_cycle, billing_days, days_summer, days_winter, prev_date, interval_length)
    key = (cur_billing_cycle.start_date[0:2] + '-' + cur_billing_cycle.start_date[6:10])
    billing_cycles[key] = cur_billing_cycle

    return billing_cycles