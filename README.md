# Zombie dancing disease tracker
 An audit log service (Service) for tracking medical information related to the widespread Zombie dancing disease.

# Problem

As the Zombie Dancing Diseases (codename "Thriller") spreads throughout the world, there is a need to track medical information related to the disease; Thus the impetus for this project. As you know a patient is infecetd with the disease by dancing with others infected with the disease; Thus spreading exponentially. Initially the patient may not show symptoms, but eventually progresses to compulsory dancing as per the 1983 music video Thriller as performed by Michael Jackson; See (1). As such it is important to track the: initial infection, progressive symptoms, treatments attempted, and spread of the disease as Thriller reaches its terminal stage. As the only known cure for the disease is the "dance off" treatment, it is also important to note if the patient was cured and what other dance was used to put the patient(s) into remission.

1) https://en.wikipedia.org/wiki/Michael_Jackson%27s_Thriller_(music_video)

# Overview

In essence the Service is a REST server with endpoint `log`, served on port 5000:

`http://<url>:5000/log`

HTTP verbs accepted by the Service are: `GET` and `POST`. `GET` is used for retrieving records and searching the database assocaited with the Service. `POST` is used for appending events to the Service.

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

# Using curl with the Service

The command-line tool `curl` can be used to interface with the Service. The Service listens for connection on port 5000 by default, requires authentication (via the `--user` curl option), and accepts input in the form of key/value pairs (the `--data` curl option). For example:

Retrieve the current set of records assocaited with the Service:

`curl http://<url>:5000/log --user <username>:<password> -X GET`

Insert a record into the Service:

`curl http://<url>:5000/log --user <username>:<password> -d "doctor=some doctor" -d "patient=some patient" -d "event_type=new_patient" -d "location=some location" -X POST`

Search for a record in the Service:

`curl http://<url>:5000/log --user <username>:<password> -d "<key>=<value>" -X GET`

# Installation

# Building

Build the wheel as normal with:

`python setup.py bdist_wheel`

# Testing


