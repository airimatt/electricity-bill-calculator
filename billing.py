from datetime import datetime, time
from decimal import Decimal, ROUND_HALF_UP
from tariff_rates import B19Rates

########################################################

# billing.py

# contains function definitions to calculate and update
# billing cycle details

########################################################


# defining date ranges for summer and winter
summer_start = (6, 1)
summer_end = (9, 30)


# define time periods in each season
time_periods = {
    "summer": {
        "peak": (time(16, 0), time(21, 0)),
        "part_peak": (time(14, 0), time(16, 0)),
        "part_peak2": (time(21, 0), time(23, 0))
    },
    "winter": {
        "peak": (time(16, 0), time(21, 0)),
        "super_off_peak": (time(9, 0), time(14, 0)),
    }
}


# checks if time is within a given time window
def in_time_window(t, window):
    t = datetime.strptime(t, "%H:%M").time()
    start, end = window
    return start <= t < end


# updates energy charge values based on datetime
def update_energy_charge_periods(cur_billing_cycle, month, date, time, usage):
    if summer_start <= (month, date) <= summer_end:
        if in_time_window(time, time_periods['summer']['peak']): # peak hours 4pm - 9pm
            cur_billing_cycle.energy_charge_periods['summer']['peak'].value += usage
        elif in_time_window(time, time_periods['summer']['part_peak']) or in_time_window(time, time_periods['summer']['part_peak2']): # partial peak hours 2pm - 4pm and 9pm to 11pm
            cur_billing_cycle.energy_charge_periods['summer']['part_peak'].value += usage
        else: # off peak hours all other hours
            cur_billing_cycle.energy_charge_periods['summer']['off_peak'].value += usage
    else:
        if in_time_window(time, time_periods['winter']['peak']): # peak hours 4pm - 9pm
            cur_billing_cycle.energy_charge_periods['winter']['peak'].value += usage
        elif (3 <= month <= 5) and in_time_window(time, time_periods['winter']['super_off_peak']): # super off peak hours 9am - 2pm March through May
            cur_billing_cycle.energy_charge_periods['winter']['super_off_peak'].value += usage
        else: # off peak hours all other hours
            cur_billing_cycle.energy_charge_periods['winter']['off_peak'].value += usage


# updates demand charge values based on datetime
def update_demand_charge_periods(cur_billing_cycle, month, date, time, demand):
    if summer_start <= (month, date) <= summer_end:
        if in_time_window(time, time_periods['summer']['peak']): # peak hours 4pm - 9pm
            cur_billing_cycle.demand_charge_periods['summer']['max_peak'].value = max(cur_billing_cycle.demand_charge_periods['summer']['max_peak'].value, demand)
        elif in_time_window(time, time_periods['summer']['part_peak']) or in_time_window(time, time_periods['summer']['part_peak2']): # partial peak hours 2pm - 4pm and 9pm to 11pm
            cur_billing_cycle.demand_charge_periods['summer']['max_part_peak'].value = max(cur_billing_cycle.demand_charge_periods['summer']['max_part_peak'].value, demand)
        # max demand includes all hours
        cur_billing_cycle.demand_charge_periods['summer']['max_demand'].value = max(cur_billing_cycle.demand_charge_periods['summer']['max_demand'].value, demand)
    else:
        if in_time_window(time, time_periods['winter']['peak']): # peak hours 4pm - 9pm
            cur_billing_cycle.demand_charge_periods['winter']['max_peak'].value = max(cur_billing_cycle.demand_charge_periods['winter']['max_peak'].value, demand)
        # max demand includes all hours
        cur_billing_cycle.demand_charge_periods['winter']['max_demand'].value = max(cur_billing_cycle.demand_charge_periods['winter']['max_demand'].value, demand)


# finalizes details of billing cycle
def finialize_billing_cycle(cur_billing_cycle, billing_days, days_summer, days_winter, prev_date, interval_length):
    offset = 24 * interval_length # (number of intervals per day)
    cur_billing_cycle.billing_days = int(billing_days // offset) or 1 # finalize previous billing cycle length (days)
    cur_billing_cycle.days_in_season['summer'] = days_summer  // offset # finalize previous billing cycle's number of summer days
    cur_billing_cycle.days_in_season['winter'] = days_winter // offset # finalize previous billing cycle's number of winter days
    cur_billing_cycle.end_date = prev_date[:10] # finalize previous billing cycle end date


# calculate monthly bills for each billing cycle
def calculate_monthly_bills(billing_cycles):

    for cycle in billing_cycles:
        cur_cycle = billing_cycles[cycle]

        # calculate customer charge
        customer_amount = Decimal(B19Rates['customer_charge_rates']['mandatory'] * cur_cycle.billing_days)
        cur_cycle.customer_charge = customer_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # calculate demand charge
        for season in cur_cycle.demand_charge_periods:
            for period in cur_cycle.demand_charge_periods[season]:
                rate = float(B19Rates['demand_charge_rates'][season].get(period, 0))
                demand_value = cur_cycle.demand_charge_periods[season][period].value
                demand_amount = Decimal(((rate * demand_value) * cur_cycle.days_in_season[season]) / (cur_cycle.billing_days or 1))
                cur_cycle.demand_charge_periods[season][period].cost = demand_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                cur_cycle.demand_charge += cur_cycle.demand_charge_periods[season][period].cost

        # calculate energy charge
        for season in cur_cycle.energy_charge_periods:
            for period in cur_cycle.energy_charge_periods[season]:
                rate = float(B19Rates['energy_charge_rates'][season].get(period, 0))
                energy_value = cur_cycle.energy_charge_periods[season][period].value
                energy_amount = Decimal(rate * energy_value)
                cur_cycle.energy_charge_periods[season][period].cost = energy_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                cur_cycle.energy_charge += cur_cycle.energy_charge_periods[season][period].cost

        # calculate total charge
        cur_cycle.total_charge = cur_cycle.customer_charge + cur_cycle.demand_charge + cur_cycle.energy_charge
