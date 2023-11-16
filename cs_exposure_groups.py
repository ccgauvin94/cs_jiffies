from pathlib import Path
import re
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from sklearn.cluster import KMeans
from cryosparc.tools import CryoSPARC
from getpass import getpass

##### Instructions #####
# Place a copy of this file in each directory you have .mdoc
# files in, load the cryosparc-tools conda environment (if using)
# and run this script: python3 cs_exposure_groups.py
#
# The major difference between this script and cs_mdoc_image_shift.py is
# that this script will do the kmeans clustering itself and update the groups
# while cs_mdoc_image_shift.py will update the image shift values of
# micrograph so that CryoSPARC can do the clusering

##### Variables #####
expected_groups = 25
cs_license = 'asdf1348-replace-me-123lkj12'
cs_hostname = 'mycryosparcinstance.mysupercoolinstitution.com'
cs_port = 39000
cs_email = 'myemail@mydomain.com'
cs_project = 'P83'
cs_workspace = 'W1'
cs_job = 'J56'
cs_job_output = 'exposure'
showplot = True

##### (il)Logic #####


#Set directory and get list of mdocs
mdoc_directory = Path('.')
mdoc_list = list(mdoc_directory.glob('**/*.mdoc'))

#Initialize list that will hold dictionary with exposure information
exposures = []

#initialize numpy array for clustering and plotting
image_shifts = np.empty(shape=(len(mdoc_list),2))


#Iterate through list of mdoc files
for i in range(len(mdoc_list)):

    #Open individual mdoc file
    with open(mdoc_list[i]) as mdoc:

        #Read each line in mdoc file
        for line in mdoc:

            #if the line matches, store the name of the file and also the image shift values into a list
            if re.search("ImageShift",line):
                shift_data = {
                    "index": i,
                    "exposure": str(mdoc_list[i]).rsplit(sep='.',maxsplit = 1)[0],
                    "x_shift": line.rsplit()[2],
                    "y_shift": line.rsplit()[3],
                    "group": 1
                    }
                exposures.append(shift_data)

#Convert dictionary x and y shift into numpy array
for i in range(len(exposures)):
    image_shifts[i,0] = exposures[i]['x_shift']
    image_shifts[i,1] = exposures[i]['y_shift']


#Kmeans clustering - probably not optimized
kmeans = KMeans(init='k-means++', n_clusters=expected_groups, n_init=10)
kmeans.fit(image_shifts)

#Assign an exposure group to each exposure in the dictionary
for i in range(len(exposures)):
    exposures[i]['group'] = kmeans.labels_[i]


#Plot the exposures and ask to proceed
if showplot == True:
    plt.scatter(image_shifts[:,0],image_shifts[:,1])
    plt.scatter(kmeans.cluster_centers_[:,0],kmeans.cluster_centers_[:,1],c='red')
    plt.show()

proceed = input("Would you like to use these exposure groups? y/n: ")
if proceed != "y":
    print("Did not confirm - exiting unceremoniously")
    quit()

#Get CS password
print("Please enter CryoSPARC password: ")
cs_password = getpass()

#Connect to CS
cs = CryoSPARC(license=cs_license, email=cs_email, password=cs_password, host=cs_hostname, base_port=cs_port)
assert cs.test_connection()

project = cs.find_project(cs_project)
job = cs.find_job(cs_project, cs_job)
cs_exposures = job.load_output(cs_job_output)
grouped_exposures = cs_exposures.copy()

for row in grouped_exposures.rows():
    for i in range(len(exposures)):
        if exposures[i]['exposure'] == row['movie_blob/path'].rsplit(sep='/')[-1]:
            row['mscope_params/exp_group_id'] = exposures[i]['group']
            row['ctf/exp_group_id'] = exposures[i]['group']
            print(row)
            break

#for row in grouped_exposures.rows():
#   print(row['movie_blob/path'], row['mscope_params/exp_group_id'])

print(grouped_exposures.fields())
project.save_external_result(
    workspace_uid=cs_workspace,
    dataset=grouped_exposures,
    type="exposure",
    name="exposure",
    slots=["mscope_params","ctf"],
    passthrough=(cs_job,cs_job_output),
    title="Grouped Exposures"
    )




