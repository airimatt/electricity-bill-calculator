from billing import calculate_monthly_bills
from preprocess import open_valid_file, read_in_data
from output import print_monthly_bills, query_bill_details


########################################################

# monthly_bill_calculator.py

# contains main function to run the monthly bill calculator
# as well as functions to read in and parse data from csv file

########################################################


# main function - calls function to run calculator
def main():
    run_calculator()


# runs the monthly bill calculator
def run_calculator():
    print("Welcome to the Monthly Bill Calculator!")
    print("Please enter the filename of the CSV data to process:")

    # take in filename from user and validate
    filename = open_valid_file()
    print("Loading in data...")
    read_in_data(filename)

    # read in data from csv file and parse into billing cycles
    billing_cycles = read_in_data(filename)

    # calculate billing details for every billing cycle
    calculate_monthly_bills(billing_cycles)

    # print summary of monthly bills for all billing cycles
    print_monthly_bills(billing_cycles)
    # query loop - while user input is not 'q' continue to ask for month-year to show billing details for that month
    query_bill_details(billing_cycles)


main()