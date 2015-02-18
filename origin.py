maxEventProcessCalls = 1000

class origin(Event):

	# prevention
    def prevent(self,by): 
		raise RuntimeError('cannot prevent an origin')
    TimePrevented = property(lambda:float('inf'))
    prevented = property(lambda:False)

	# un-prevention
    def unpreventALL(self): pass
    def unprevent(self,by): pass

    # the origin is time = 0 by definition
    time = property(lambda:0)

	# reference property 
    reference = property(lambda:raise RuntimeError('the origin has no reference event'))

	# return the origin (A.K.A. self) 
    origin = property(lambda self: self)

    def __init__(self,*args,**kwargs):
        """initialzation for an event origin."""
        super(origin, self).__init__(*args,**kwargs)
        self.eventState = ()
    
    def processEvents(self):
        """ this function calls all the events in order of time and allows them 
            to be processed, which allows events to be responsive to one
            another. 

            Specifically, some events may be dependent on the occurance
            of another event.  For example, Tubal ligation is not possible
            after tubes are removed, and women may be at lower risk after
            a tubal ligation.

            Event processing happens in order by time, and the event should
            only respond by deleting it's reference (in the case that the event
            does not happen because of an earlier event), or (if it is a 
            distributed event),  by accelerating (decelerating) it's distribution
            at the time of the event that event that affect's it's risk of 
            occuring by calling event.accelerate() [or better still, by calling
            event.setChangePoints() with a list of event ages and RR's]
        """

        if len(self.eventState):
            raise RuntimeError('nested calls to origin.process() are not allowed')

        events = self.getEvents(type=lambda x:True,
                                    includePrevented=True,
                                    includeNoneTimes=True,
                                    deepQuery=True,
                                    ordered=False)
        eventState = tuple( (e.time,e) for e in events)
        self.eventState = eventState
        
        processedEvents = 0
        while True:
            for e in events: 
                # --------------------------------------------------
                # It's important to avoid processing an event twice
                # with the same set of prior events, in order to prevent
                # infintite update loops.  
                # so we'll record a list of events that occured before this on
                # at the outset, and only re-update the event in case the set 
                # of prior events has changed between loops. 
                # --------------------------------------------------
                # get a list of events that occured prior to the current event
                if e.time is None:
                    # any event with a numeric time occured before an event
					# with a None time (None == Inf).
                    priorEvents = self.getEvents(
							type=lambda x: True ,
							deepQuery=True,
							includeNoneTimes=False)
                else:
                    priorEvents = self.getEvents(
							type=lambda x: x.time is not None and x.time < e.time)
                # the tuple will change if the event Times change...
                priorEventsTuple = tuple( (e.time,e) for e in priorEvents)
                if hasattr(e,'_processedFor'):
                    if e._processedFor == priorEventsTuple:
                        # don't process the same event twice.  (otherwise a 
						# race condition may occure)
                        continue
                    else: 
                        # the event history has changed, so we need to
						# re-set the event to it's initial state so as to
						# keep the event processsing itempotent.

                        # FIXME: this needs to be more generic than a call
						# to a method specific to the DistributedEvent
						# class. Something like event.Reset, perhaps
                        if hasattr(e,'_resetCDF'):
                            e._resetCDF()
                e._processedFor = priorEventsTuple
                eventTimeBeforeProcessing = e.time
                e.process()
                if eventTimeBeforeProcessing != e.time:
                    processedEvents += 1
                if processedEvents > maxEventProcessCalls:
                    raise RuntimeError('Number of event.process() calles exceeds maxEventProcessCalls.  Possible race condition.')

            events = self.getEvents(type=lambda x:True,
                                        includePrevented=True,
                                        includeNoneTimes=True,
                                        deepQuery=True,
                                        ordered=False)
            eventState = tuple( (e.time,e) for e in events)
            if eventState == self.eventState:
                break
            self.eventState = eventState

        #RESET THE eventsState...
        self.eventState = ()

