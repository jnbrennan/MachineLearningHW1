import csv as csv
import numpy as np

# Open train.csv file into Python object
csv_file_object = csv.reader(open('/Users/Jessica/Documents/Python/train.csv', 'rb'))
# Skip first line/header
header = csv_file_object.next()

# Run through each row in csv file, add to data list
data=[]
for row in csv_file_object:
    data.append(row)

# Convert list to array
data = np.array(data)

# Determine survivor proportion for all
number_passengers = np.size(data[0::,1].astype(np.float))
number_survived = np.sum(data[0::,1].astype(np.float))
proportion_survivors = number_survived / number_passengers

# Modify data so everything >= 40 is set to 39
fare_ceiling = 40
data[data[0::,9].astype(np.float) >= fare_ceiling, 9] = fare_ceiling -1.0

# Get number of fare brackets
fare_bracket_size = 10
number_of_price_brackets = fare_ceiling / fare_bracket_size

# Get number of classes
number_of_classes = len(np.unique(data[0::, 2]))

# Create survival table (filled with zeros)
survival_table = np.zeros([2, number_of_classes, \
                           number_of_price_brackets] , float)

# Clump passangers into groups bassed off of gender, class, and ticket price
for i in xrange(number_of_classes):
    for j in xrange(number_of_price_brackets):
        women_only_stats = data[(data[0::, 4] == "female")  \
                                & (data[0::, 2].astype(np.float) == i+1) \
                                & (data[0:, 9].astype(np.float)  \
                                   >= j*fare_bracket_size)  \
                                & (data[0:,9].astype(np.float)  \
                                   < (j+1)*fare_bracket_size)  \
                                , 1]
        men_only_statis = data [(data[0::, 4] != "female")  \
                        & (data[0::, 2].astype(np.float) == i+1)  \
                        & (data[0:, 9].astype(np.float)  \
                           >= j*fare_bracket_size)  \
                        & (data[0:, 9].astype(np.float)  \
                           < (j+1)*fare_bracket_size)  \
                        , 1]
        # Calculate proportion of survivors for particular combo
        # of criteria then put into a survivor table
        survival_table[0, i, j] = np.mean(women_only_stats.astype(np.float))
        survival_table[1, i, j] = np.mean(men_only_statis.astype(np.float))
        
# Set non numbers in table to 0
survival_table[ survival_table != survival_table ] = 0

# Set predictions, <0.5 they don't survive, >= 0.5 they do
survival_table[ survival_table < 0.5 ] = 0
survival_table[ survival_table >= 0.5 ] = 1

# Read in test file, skip header, write to new file
test_file = open('/Users/Jessica/Documents/Python/test.csv', 'rb')
test_file_object = csv.reader(test_file)
header = test_file_object.next()
predictions_file = open("genderclassmodel.csv", "wb")
predictions_file_object = csv.writer(predictions_file)
predictions_file_object.writerow(["PassengerID", "Survived"])

# Loop through each bin to see if ticket falls in it, then assign
for row in test_file_object:
    for j in xrange(number_of_price_brackets):
        try:
            row[8] = float(row[8])
        except:
            bin_fare = 3 - float(row[1])
            break
        if row[8] > fare_ceiling:
            bin_fare = number_of_price_brackets - 1
            break
        if row[8] >= j * fare_bracket_size and row[8] <  \
                (j+1) * fare_bracket_size:
            bin_fare = j
            break
# Grab rest of relevent elements in survival_table
    if row[3] == 'female':
        predictions_file_object.writerow([row[0], "%d" % \
                                          int(survival_table[0, float(row[1])-1, bin_fare])])
    else: # male
        predictions_file_object.writerow([row[0], "%d" % \
                                          int(survival_table[1, float(row[1])-1, bin_fare])])

# Close out files
test_file.close()
predictions_file.close()