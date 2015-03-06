## Description

A python module which generates random event sequences which simultaneously 
recapitulate marginal (age conditional) and proportional hazards.

## Dependencies
- A yaml package for python.  I use PyYAML which can be downloaded [here](http://pyyaml.org/wiki/PyYAML).

## Overview

The Monte Carlo Proportional hazards (MCPH) model is designed 
as a framework for randomly generating timelines of events 
from the net hazards of each individual event*, and the 
hazards ratios that describe the relationships between events 
being modeled.   

The MCPH model includes a specific framework with two distinct 
classes of events:  

### The Origin Event

An *origin* is a special event which is used to define *absolute time*
and is used to describe the first instance when a modeled unit 
can experience one or more events.  For example, if we are modeling 
the cancer prevention, the model unit will be an individual perrson
and the origin may represent the birth of person because cancer 
diagnoses and cancer preventions may not occure prior to birth but 
may occure soon thereafter.

### The Timed Events

A timed event (referred to simply as an 'event' hereafter) describes
an event of intereset which happens at a given time.  To continue 
our example, If we are modeling cancer prevention, cancer diagnosis 
is modeled as a diagnosis event, and cancer preventions are also 
modeled as events. 

Becuase it may be convenient to define the timing of certian events 
in relaative terms, individual events may be defined relative to 
the origin (Age at diagnosis = 62), or with respect to another event 
(death from cancer = 14 years after diagnosis).

The relative timing of events is kept track of using the dot operator
to assign events as attributes of other events or of the orign.  In this
example, we'll create a model which includes (1) diagnosis with ovarian 
cancer (2) death from ovarian cancer (3) death from other causes and (4) 
salpingectomy (removal of the fallopian tubes [which may have a 
risk reducing effet on ovarian cancer].  In this example, we'll set up
the framework witch desribes how the events relate to one another 
without worrying about parameterizing the timing of the events.


	# create a new origin 
	Person = Origin()

	# create the individual events
	OvarianCancer = Event(...) # parameters to be discussed below
	CancerDeath = Event(...) 
	Salpingectomy = Event(...)
	DeathFromOtherCauses = Event(...)

	# Relate the events to each other using the dot operator
	OvarianCancer.CancerDeath = CancerDeath
	Person.OvarianCancer = OvarianCancer
	Person.Salpingectomy = Salpingectomy


In the above code, after creating the events, we've specified that the
time of cancer death is measured relative to the timing of cancer 
diagnosis and that time timing of salpingectomy and death from 
other cuases is specified relative to the person's birth


