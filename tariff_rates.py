from decimal import Decimal

########################################################

# tariff_rates.py

# contains dictionary defining tariff rates
# (as of now only B19 rates are defined)

########################################################



B19Rates = {
    'customer_charge_rates' : {
        'mandatory' : Decimal('59.63519'),
        'voluntary' : Decimal('11.65358') # not used in this program
    },
    'demand_charge_rates' : {
        'summer' : {
            'max_peak': Decimal('54.17'),
            'max_part_peak': Decimal('11.75'),
            'max_demand': Decimal('39.22')
        },
        'winter' : {
            'max_peak': Decimal('3.20'),
            'max_demand': Decimal('39.22')
        }
    },
    'energy_charge_rates' : {
        'summer' : {
            'peak': Decimal('0.21867'),
            'part_peak': Decimal('0.16493'),
            'off_peak': Decimal('0.12692')
        },
        'winter' : {
            'peak': Decimal('0.18454'),
            'off_peak': Decimal('0.12677'),
            'super_off_peak': Decimal('0.04927')
        }
    }
}
