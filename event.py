"""
    ==============================================
    # WARNING, NOT ALL OF WHAT FOLLOWS IS ACCURATE
    # for the current implemntation of the Event
    # class
    ==============================================

    An Event is both an event and a place holder for a timeline.
    The origin of the timeline is considered to be the time of the event
    and any events it contains timed relative to that origin. 

    As an example, a person is merely a timelint that begins at birth 
    (time = 0).  likewise, a tumor is a timelint with the origin at the 
    time of diagnosis.  

    the origin of the timeline is always considered to be zero, which is
    to say that the timing of events within a timeline should be relative
    to the time at that event.  

    For example, if a woman is diagnosed at a tumor at time 55, which will cause
    her to die 12 years later, that recorded as 


    because Events can nest other events, they nesting is kept track 
    of when using the dot operator (as in someone.tumor) which makes takes care
    of a lot of accounting that goes on in the model. 

    The following example may help:

    ==============================================
    Example: shifting sub-timelines into local
            time coordinates.
    ==============================================

    tumor = Event(type='tumor',id='ovarianCancer',time = 55) # the origin of the tumor relative to it's reference
    deathFromCancer = Event(time = 12)
    tumor._addEvent(deathFromCancer)
    someone._addEvent(tumor)

    # Next, we access the deathFromCancer timeline with the dot operator, 
    # so the origin of the person (birth time = 0) to the tumor orign (time at 
    # diagnosis = 55) and the deathFromCancer origin (12 years after dx

    print someone.tumor.deathFromCancer.time # prints 67 

    ==============================================
    End Example
    ==============================================

    because timelines have this nice property of keeping track of nested
    timelines, we need to prevent timline instances from duplicating this 
    calculation.  Hence, we need to freeze the timeline when it has been 
    accessed as a child timeline. 

    ==============================================
    Example: potential double counting situation
    ==============================================

    tumor = Event(type='tumor',id='ovarianCancer',time = 55) # the origin of the tumor relative to it's reference
    deathFromCancer = Event(time = 12)
    tumor._addEvent(deathFromCancer)
    someone._addEvent(tumor)

    # then later: 
    thisTumor = someone.tumor
    ...
    ...
    someone.tumor = thisTumor 

    ==============================================
    End Example
    ==============================================
    in the above example, if we didn't keep track
    of the reference timeline, we would end up shifting
    the originof thisTumor twice and our ages at
    events would get all screwed up

    ==============================================
    time v. reftime
    ==============================================
    Because all timelines are considered to be 
    within the context of a person's life, the 
    'global' cordintes of a timeline refers to 
    that person's time at the event.  

    The local coordinates, however, can be measured
    with respect to some event that defines an reftime.
    The Event Class has an implicit reftime 
    which is the time at the 'even'.  
    
    to get the global coordinates, use 'getAge' methods
    , and to get local coordinates, ust the 'getTime' 
    methods.
    
"""

from math import isinf
from operator import attrgetter
from types import NoneType
import pdb

inf = float('inf')

class Event(object):
    """ 
    most of what follows is not longer accurate.  Here is what's current:
    ==================================================
    * an event is an object with 3 special (public) properties: 

        'reference': another event that serves as the 
                reference time for this event.  References
                can be followed from child to parent
                until a global (person) object is reached.
                The global object cannonically does not have 
                a reference event.

        'reftime': the time between this event and 
            the reference event (negative if this event occured
            first).

        'time': a calculated property := time between
                this event and the global event (birth),
                *iif* a global event is at the top of the 
                reference chain.

    and a couple of sepcial methods:
        'getEvent()': returns a named event.
        'getEvents()': returns a (possibly empty) list 
                of events with a set of common characteristics

    Events *may* have a reference event, in which case the 
    event is a child of it's reference.  
    
    there are three ways to set a reference event on an event:
    (1) in the init method [ child = Event(reference=parent) ]
    (2) via the child's reference attrubute [ child.reference = parent ]
    (3) via attribute assignment  [ parent.foo = child ]

    Note that the first two methods to not assign a name 
    to the event.  

    The link between parnet and child can always be removed 
    via 'del child.reference', and in the case that the third
    assignment option was used, 'del parent.foo' will also 
    remove the link between child and parent.

    the final aspect of an event is that attribute assignment 
    can be used to set the reference (parent / child) 
    relationship.  (e.g. parent.foo =  child) sets the 
    parent / child relation and names the event 'foo'.

    

    ==================================================

    """

    # default values for time and reftime

    def __init__(self,
            # the time between the reference event and this event
            reftime=None,

            # the reference object
            reference=None,

            # a string, tuple of strings, or list of strings to aid
            # in searching for events. 
            type=()): 

        # store the reference event
        if reference is not None:
            self.reference = reference # implicicitly uses the reference setter property
            `
        # the time of the event relative to the reference frame
        if reftime is not None:
            self.__dict__['reftime'] = reftime 
            `
        # store the 'type' tuple
        if isinstance(type,str):
            type = (type,)
        elif isinstance(type,list):
            type = tuple(type)
        self.type = type # a tuple that names the event type

        # initialize the childen and prevented by lists
        self._children = []
        self._preventedBy = []

    # --------------------------------------------------
    # prevented properties
    # --------------------------------------------------
    def unpreventALL(self):
        self._preventedBy = []

    def unprevent(self,by):
        for(i in range(len(self._preventedBy)-1,-1,-1)) 
            if self._preventedBy is by:
                del self._preventedBy[i]

    def prevent(self,by):
        if inherits(by,origin):
            raise RuntimeError('An event cannot be prevented by an orign')
        if self is by:
            raise RuntimeError('An event cannot be prevented by itself')
        if by not in self._preventedBy :
            self._preventedBy.append(by) 

    def _getTimePrevented(self):
        if(len(self._preventedBy)):
            return min([x.time for time in self._preventedBy])
        else :
            return float('inf')

    TimePrevented = property(_getTimePrevented)

    def _prevented (self):
        """ An event is prevented if any of the prevention events 
            occure prior to the event in the absence of prevention 
            events.
        """ 
        return float(self) > min(x.time for x in self._preventedBy])
    prevented = property(_prevented)

    # --------------------------------------------------
    # time property
    # --------------------------------------------------

    def _getTime(self):
        if 'reference' not in self.__dict__:
            raise RuntimeError("Attempt to GET the time of an event before setting the event's reference attribute, OR no global reference found.")

        refTime = self.reference.time 
        if self.reftime is None or refTime is None:
            return None
        else:
            return float(self.reftime) + refTime

    time = property(_getTime)

    # --------------------------------------------------
    # redraw method
    # --------------------------------------------------
    def redraw(self):
        """call the redraw method on self.reference.time or self.reference.reftime"""
        try:
            self.reference.time.redraw()
        except AttributeError:
            pass

        try:
            self.reference.reftime.redraw()
        except AttributeError:
            pass

    # --------------------------------------------------
    # Attribute Setter
    # --------------------------------------------------
    def __setattr__(self, name, value): 
        """ The Set Attr method, which is reponsible for setting 
            the double link between events for statements like: `e1.e2 = e2`
        """

        if name in ('reference',):
            # python calles setter methods in this order, so we have to bypass __setattr__
            # in order to get the property getter and setter methods defined below to handle 
            # the assighment. See this page for details:
            # 
            #       http://stackoverflow.com/questions/15750522/class-properties-and-setattr 

            object.__setattr__(self, name, value)
            return

        if isinstance(value,Event):
            if ('reference' in value.__dict__ 
                    and value.reference is not self):
                raise AttributeError('Attempt to add two reference to a single event')

            # PREVENT CIRCULAR PARENT/CHILD REFERENCES 
            tmp = value
            while 'reference' in tmp.__dict__:
                if(inherits(tmp,origin))
                    break
                if tmp is self:
                    raise ValueError("Circular Reference Error: attempt to add a Event as a child of an ancestor.")
                tmp = tmp.reference

            # ADD SELF AS THE EVENT'S NEW 'REFERENCE' ATTIRUBTE
            value.reference = self

        self.__dict__[name] = value


    # --------------------------------------------------
    # Attribute Deleter
    # --------------------------------------------------

    def __delattr__(self, name): 
        if name not in self.__dict__:
            raise AttributeError(name)

        if name == 'reference':
            # python calles setter methods in this order, so we have to bypass __setattr__
            # in order to get the property getter and setter methods defined below to handle 
            # the assighment. See this page for details:
            # 
            #       http://stackoverflow.com/questions/15750522/class-properties-and-setattr 
            object.__delattr__(self, name)
            # this propogates the delete on to the '__delReferenceEvent()' method below
            return

        if isinstance(self.__dict__[name],event): 
            # NO CIRCULAR REFERENCES PLEASE, hence the following line
            # is NOT !!:  self.__dict__[name].reference
            del self.__dict__[name].__dict__['reference']

        del self.__dict__[name] 

    # --------------------------------------------------
    # 
    # --------------------------------------------------
    def _origin(self):
        """ Retruns the origin event which is an ancestor to self. """
        this = self
        while True:
            if 'reference' not in self.__dict__:
                return None
            reference = self.__dict__['reference']
            if isinstance(reference,origin):
                return reference
            else: this = reference
    origin = property(_origin)

    # --------------------------------------------------
    # stubs for pre and post processing 
    # --------------------------------------------------
    def preprocess(self):
        """ preprocess() is called when the event is initialized.  it is
            responsible for initializing any values required for processing
            and/or eligibility testing.  before the person event is tested for
            enrollment eligibility, and before the personEventProcessors in the
            decisionRule are called.
        """
        pass # to be over-written by sub-classes

    def process(self):
        """ process() is called in order to handle the conditional events.
            For example It's not possible for a tubal ligation (TL) to occure
            after the tubes are removed (BS), so the TL should set it's time to
            None in it's "process()" method when a BSO occures before the TL.

            The Process() method should be used to modifiy the event that it
            is called on, and not other events.  The cascasde of
            event.process() calles proceeds cronologically from the minimum
            of [a] the time of the event before calling event.process(), [b]
            the time of the event after calling event.process() and [c] the
            return value from process (optional).

        """
        pass # to be over-written by sub-classes

    def postprocess(self):
        """ postprocess() is called after all the event generators have been
            called, and after the person event is qualified for enrollment
            eligibility.  It is also called each time that the time of the event
            is reset.

            postprocess() is therefor good for things like assigning marker
            levels, which are expensive to generate, and not needed to
            determine eligibility or when the tumor does not have an time at
            diagnosis.  with a diagnosis, etc.,
            
            The timing of this or any other event that existed during
            processing should *NOT* be modified here.

            Postprocess() is called *after* eligibility testing, so it may
            not be called on events from ineligible individuals.
        """
        pass # optionally, to be over-written by sub-classes

    # --------------------------------------------------
    # Reference event property
    # --------------------------------------------------

    def __setReferenceEvent(self,reference):

        # PREVENT CIRCULAR PARENT/CHILD REFERENCES 
        if reference is self:
            raise ValueError("Attempt to add a Event as it's own reference point. Circular references are forbidden")
        ancestor = reference
        while True:
            if ancestor is self:
                raise ValueError("Attempt to add a Event as a child of an ancestor. Circular references are forbidden")
            if not 'reference' in ancestor.__dict__:
                break
            ancestor = ancestor.reference

        if 'reference' in self.__dict__:
            print 'deleting child.reference'
            del self.reference

        self.__dict__['reference'] = reference

        # *may* need to complete the loop
        if not self in reference.getEvents():
            reference.__dict__['_children'].append(self)
            

    def __getReferenceEvent(self):
        return self.__dict__['reference']

    def __delReferenceEvent(self):
        # since we don't know if this event is is even named, we have 
        # to delete it from the reference based on it's value. Specifically
        # this event (self) can be on of:
        #    [a] this.__data__.[namedChild]
        #    [b] this.__data__._children[this.__data__._children.index(child)]
        if self in self.__dict__['_children']:
            del self.__dict__['_children'][self.__dict__['_children'].index(self)]
        tmpKeys = []
        for key,value in self.__dict__.iteritems():
            if value is self:
                tmpKeys.append(key)

        for key in tmpKeys:
            del self.__dict__[key]
        # now delete the reference from __dict__
        del self.__dict__['reference']

    reference = property(__getReferenceEvent,
            __setReferenceEvent,
            __delReferenceEvent)

    # --------------------------------------------------
    # event query methods
    # --------------------------------------------------

    def getEvent(self,name):
        out = self.__dict__[name]
        if not isinstance(out,Event):
            raise KeyError("Event instance has no event named '"+name[0]+"'.")

    def getEvents(self,
            type=None,
            deepQuery=False,
            includePrevented=False,
            includeNoneTimes=False,
            ordered=False,
            first=False):
        """ returns a list of events with type 'type' """
        try:
            out = self.__dict__['_children'] + [e for e in self.__dict__ if isinstance(e,Event) ]
        except: pdb.set_trace()
        if not includeNoneTimes:
            out = [e for e in out if e.time is not None]
        if not includePrevented:
            out = [e for e in out if not e.prevented]
        if deepQuery: 
            # NOTE THAT this looping trick depends on not haveing circular references in the events
            for e in out:
                out.extend(e.getEvents(type=type, deepQuery=deepQuery, ordered=ordered, first=first))

        if type:
            if hasattr(type,'__call__'):
                out = [e for e in out if type(e)]
            else:
                out = [e for e in out if type in e.type ]

        if ordered or first:
            out  = sorted(out, key=lambda x: x.time if x.time is not None else inf)
        if first:
            if len(out):
                return out[0]
            else:
                return None
        else:
            return out



# module test code
if __name__ == '__main__':

    import sys

    b = Event()

    # ----------------------------------------
    msg = 'bad time assignment (no reference event)'
    sys.stdout.write(msg+"\r" )
    try:
        b.time = 5
    except RuntimeError:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )

    # ----------------------------------------
    msg = 'bad time query (no reference event)'
    try:
        _ = b.time
    except RuntimeError:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )

    # ----------------------------------------
    msg = 'self reference assignment'
    sys.stdout.write(msg+"\r" )
    try:
        b.reference = b
    except ValueError as e:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )

    # ----------------------------------------
    msg = 'valid reference assignment'
    sys.stdout.write(msg+"\r" )
    a = Event()
    try:
        b.reference = a
    except ValueError as e:
        sys.stdout.write(msg + "...Failed\n" )
    else:
        sys.stdout.write(msg + "...Passed\n" )

    # ----------------------------------------
    msg = 'circular reference assignment'
    sys.stdout.write(msg+"\r" )
    try:
        a.reference = b
    except ValueError as e:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )

    # ----------------------------------------
    msg = 'no origin'
    sys.stdout.write(msg+"\r" )
    try:
        b.time = 5
    except RuntimeError:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )

    # ----------------------------------------
    msg = 'no origin'
    try:
        _ = b.time
    except AttributeError:
        sys.stdout.write(msg + "...Passed\n" )
    else:
        sys.stdout.write(msg + "...Failed\n" )


    # ----------------------------------------
    a.isGlobalReference = True
    msg = 'good time assignment '

    sys.stdout.write(msg+"\r" )
    try:
        b.time = 5
    except AttributeError:
        sys.stdout.write(msg+"...Failed\n" )
    else:
        sys.stdout.write(msg+"...Passed\n" )


    c = Event(reference=b,time = 11)
    assert c.reftime == 6

    # ----------------------------------------
    a.isGlobalReference = True
    msg = 'deleting global event '

    sys.stdout.write(msg+"\r" )
    try:
        del b.reference
    except AttributeError:
        sys.stdout.write(msg+"...Failed\n" )
    else:
        sys.stdout.write(msg+"...Passed\n" )

    # ----------------------------------------
    msg = 'getting time of secondary event after deleting the global event '

    sys.stdout.write(msg+"\r" )
    try:
        b.time
    except RuntimeError:
        sys.stdout.write(msg+"...Passed\n" )
    else:
        sys.stdout.write(msg+"...Failed\n" )


    # ----------------------------------------
    msg = 'getting time of tertiary event after deleting the global event '

    sys.stdout.write(msg+"\r" )
    try:
        c.time
    except RuntimeError:
        sys.stdout.write(msg+"...Passed\n" )
    else:
        sys.stdout.write(msg+"...Failed\n" )

    # ----------------------------------------
    msg = 'adding the global by named assignment'

    sys.stdout.write(msg+"\r" )
    try:
        a.tumor = b
    except :
        sys.stdout.write(msg+"...Failed\n" )
    else:
        sys.stdout.write(msg+"...Passed\n" )

    # ----------------------------------------
    msg = 'getting time of secondary event after attribute assignment the global event '

    sys.stdout.write(msg+"\r" )
    try:
        b.time
    except :
        sys.stdout.write(msg+"...Failed\n" )
    else:
        sys.stdout.write(msg+"...Passed\n" )


    # ----------------------------------------
    #a.isGlobalReference = True
    msg = 'circular reference (as a named attribute)'

    sys.stdout.write(msg+"\r" )
    try:
        c.person = a
    except RuntimeError:
        sys.stdout.write(msg+"...Passed\n" )
    else:
        sys.stdout.write(msg+"...Failed\n" )

    # ----------------------------------------
    #a.isGlobalReference = True
    msg = 'deleting global event (as a named attribute)'

    sys.stdout.write(msg+"\r" )
    try:
        del b.reference
    except AttributeError:
        sys.stdout.write(msg+"...Failed\n" )
    else:
        sys.stdout.write(msg+"...Passed\n" )

    # ----------------------------------------
    msg = 'getting time of secondary event after deleting the global event '

    sys.stdout.write(msg+"\r" )
    try:
        b.time
    except RuntimeError:
        sys.stdout.write(msg+"...Passed\n" )
    else:
        sys.stdout.write(msg+"...Failed\n" )


    # ----------------------------------------
    msg = 'getting time of tertiary event after deleting the global event '

    sys.stdout.write(msg+"\r" )
    try:
        c.time
    except RuntimeError:
        sys.stdout.write(msg+"...Passed\n" )
    else:
        sys.stdout.write(msg+"...Failed\n" )

# ValueError



