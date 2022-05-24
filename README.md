(An example audit log service used to demonstrate Python proficiency for a job application. )

# Zombie dancing disease tracker
 An audit log service (Service) for tracking medical information related to the widespread Zombie dancing disease.

# Problem

As the Zombie Dancing Diseases (codename "Thriller") spreads throughout the world, there is a need to track medical information related to the disease; Thus the impetus for this project. As you know a patient is infected with the disease by dancing with others infected with the disease; Thus spreading exponentially. Initially the patient may not show symptoms, but eventually progresses to compulsory dancing as per the 1983 music video Thriller as performed by Michael Jackson; See (1). As such it is important to track the: initial infection, progressive symptoms, treatments attempted, and spread of the disease as Thriller reaches its terminal stage. As the only known cure for the disease is the "dance off" treatment, it is also important to note if the patient was cured and what other dance was used to put the patient(s) into remission.

1) https://en.wikipedia.org/wiki/Michael_Jackson%27s_Thriller_(music_video)

# Overview

In essence the Service is a REST server with endpoint `log`, served on port 5000:

`http://<url>:5000/log`

HTTP verbs accepted by the Service are: `GET` and `POST`. `GET` is used for retrieving records and searching the database associated with the Service. `POST` is used for appending events to the Service.

## Note, debug mode

For the purposes of this project the Service has been left in "debug" mode. As such debugging information is printed to the console and a test account has been automatically added to the Service for testing. The test account has the username `test` and the password `test`. To disable debug mode set `_DEBUG` to `False` in `__main__.py`.

# Schema

New records appended to the Service should adhere to the following schema. Required fields for each event submitted should include: "doctor" (a string), "patient" (string), "event_type" (see below for standard event types; but also a user-defined string is possible), and "location" (string). Other optional fields include: "date_time" (a string indicating a date, or a date object), and "notes" (string). Other fields beyond these required and optional fields are also accepted. If not specified the "date_time" field is appended as the current date and time. If "notes" are not added, they are appended to the record with a value of "None". Note that field names should not being with an underscore character (\_) as fields of this type are reserved for internal use. Also note that fields "\_user" and "\_timestamp" are automatically appended to each record. A summary of the schema is presented below:

```
{
 "doctor" : "string", #required
 "patient" : "string", #required
 "event_type" : ["new_patient", "patient_infected", "treatment", "patient_terminal", "other"] | "string", #required
 "location" : "string", #required
 "date_time" : "date" | "string", #optional
 "notes" : "string", #optional
 ...
}
```

# Sample audit trail

To demonstrate th6e functionality of the Service, a sample audit trail is discussed; Or, in other words, a short story of events that might be documented with the Service. For example, consider Dr. Smith, with a practice in Calgary Alberta. They begin treating a new patient Albus Dumbledor ("event_type": "new_patient"), and confirm the patient's infection ("new_patient": "patient_infected"). Dr. Smith proposes a standard treatment, as well as an experimental treatment of having the patient dance the Watusi to mitigate symptoms ("event_type" : "treatment"). This fails and the patient is declared terminal and expires from exhaustion after dancing nonstop for days ("event_type" : "patient_terminal"). Dr. Smith notes that the Watusi-treatment was somewhat effective in treatment, and makes a note ("event_type" : "other"), and recommends a study to evaluate the efficacy of the Watusi-treatment with a randomized controled trial ("event_type" : "proposal"). As such the audit trail of such a sequence of events would be:

```
[                                                 
    {                                             
        "doctor": "Dr. Smith",                  
        "patient": "Albus Dumbledor",                
        "event_type": "new_patient",              
        "location": "Calgary, AB",              
        "_user": "smith",                          
        "date_time": "April 1st 2022",
        "notes": null,                            
        "_timestamp": "2022-04-01"
    },
    {                                             
        "doctor": "Dr. Smith",                  
        "patient": "Albus Dumbledor",                
        "event_type": "patient_infected",              
        "location": "Calgary, AB",              
        "_user": "smith",                          
        "date_time": "April 3rd 2022",
        "notes": null,                            
        "_timestamp": "2022-04-03"
    },
    {
        "doctor": "Dr. Smith",                  
        "patient": "Albus Dumbledor",                
        "event_type": "treatment",
        "location": "Calgary, AB",              
        "_user": "smith",                          
        "date_time": "April 5th 2022",
        "notes": "beginning standard treatment",                            
        "_timestamp": "2022-04-06"
    },
    {
        "doctor": "Dr. Smith",                  
        "patient": "Albus Dumbledor",                
        "event_type": "treatment",
        "location": "Calgary, AB",              
        "_user": "smith",                          
        "date_time": "April 7th 2022",
        "notes": "beginning Watusi-treatment. Patient is instructed to dance the Watusi twice-daily and call me in the morning.",                            
        "_timestamp": "2022-04-10"
    },
    {
        "doctor": "Dr. Smith",                  
        "patient": "Albus Dumbledor",                
        "event_type": "patient_terminal",
        "location": "Calgary, AB",              
        "_user": "smith",                          
        "date_time": "April 22nd 2022",
        "notes": null,
        "_timestamp": "2022-04-10"
    },
    {
        "doctor": "Dr. Smith",
        "patient": "Albus Dumbledor",
        "event_type": "other",
        "location": "Calgary, AB",
        "_user": "smith",                          
        "date_time": "April 29th 2022",
        "notes": "patient seemed to respond well to the Watusi, gaining an extra week of good health before sucumbing to code-name 'Thriller'",
        "_timestamp": "2022-04-10"
    },
    {
        "doctor": "Dr. Smith",
        "patient": "Albus Dumbledor",
        "event_type": "proposal",
        "location": "Calgary, AB",
        "_user": "smith",                          
        "date_time": "April 29th 2022",
        "notes": "Recommend a full-scale clinical trial of the Watusi-protocol. Intervention documented in attached DOI.",
        "_timestamp": "2022-04-10",
        "doi": "doi:10.1038/nphys1170",
    },
]                                                 
```

# Using curl with the Service

The command-line tool `curl` can be used to interface with the Service. The Service listens for connection on port 5000 by default, requires authentication (via the `--user` curl option), and accepts input in the form of key/value pairs (the `--data` curl option). For example:

Retrieve the current set of records associated with the Service:

`curl http://<url>:5000/log --user <username>:<password> -X GET`

Insert a record into the Service:

`curl http://<url>:5000/log --user <username>:<password> -d "doctor=some doctor" -d "patient=some patient" -d "event_type=new_patient" -d "location=some location" -X POST`

Search for a record in the Service:

`curl http://<url>:5000/log --user <username>:<password> -d "<key>=<value>" -X GET`

# Installation

Download the latest release and install with pip:

`pip install zombie_dance_disease_tracker.whl`

The code has been tested on the latest Ubuntu release.

# Building

Clone the repository, and build the wheel as normal with:

`python setup.py bdist_wheel`

# Testing

Tests can be found in the `test` directory. Testing is done with `pytest` (https://docs.pytest.org/). Testing requires the additional package `xprocess` (https://github.com/pytest-dev/pytest-xprocess) and `curl`. Testing depends on finding the python executable, which it assumes is named `python`. Once these steps are complete, then testing can be completed via: `python -m pytest`.
