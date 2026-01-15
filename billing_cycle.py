class ValueCost:
    def __init__(self):
        self.value = 0
        self.cost = 0


class BillingCycle:
    def __init__(self, start_date: str):
        self.start_date = start_date
        self.end_date = None
        self.energy_charge_periods = None
        self.demand_charge_periods = None
        self.days_in_season = { 'summer': 0, 'winter': 0 }
        self.billing_days = 0
        self.customer_charge = 0
        self.demand_charge = 0
        self.energy_charge = 0
        self.total_charge = 0


    def initialize_energy_charge_periods(self, start_date, cur_billing_cycle):
        month = int(start_date[0:2])
        day = int(start_date[3:5])

        cur_billing_cycle.energy_charge_periods = {
            "summer" : {
                "peak": ValueCost(),
                "part_peak": ValueCost(),
                "off_peak": ValueCost()
            },
            "winter" : {
                "peak": ValueCost(),
                "off_peak": ValueCost(),
                "super_off_peak": ValueCost()
            }
        }


    def initialize_demand_charge_periods(self, start_date, cur_billing_cycle):
        month = int(start_date[0:2])
        day = int(start_date[3:5])

        cur_billing_cycle.demand_charge_periods = {
            "summer" : {
                "max_peak": ValueCost(),
                "max_part_peak": ValueCost(),
                "max_demand": ValueCost()
            },
            "winter" : {
                "max_peak": ValueCost(),
                "max_demand": ValueCost()
            }
        }

