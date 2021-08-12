## Structure
```bash
├── context # user/developer's contact with signal processing methods
├── core # core data objects will be managed by context
├── tests 
└── tools # additional tools that don't fit in core or context
```

## Implementation
+ The context will have one global environment and one or more processors.
+ The environment
  + is a key-value based dictionary of variable names and their data.
  + the variable name is generic and only the concrete environment's define the
        rules of a variable name.
  + For example, 
    + considering a codacuda DS, the variable name is a series of alpha-numeric characters
        that the iplotDataAccess module can understand.
    + considering an imasuda DS, the variable name is a forward-slash separated sequence of
        words or numbers (in case of AoS). Obviously, only the iplotDataAccess module can
        understand it.
  + The value in the dictionary for a given key is a `core/Signal` object
  + We will have to somehow initialize a `core/Signal` object populated with the time, data members prior
        to evaluating the expression.
  + Without copying the iplotDataAccess/dataObj data.
+ The processor 
  + will have access to the global environment of the context it is registered with.
  + will need an input expression. (Something like `${SignalName-X-Y-Z}+${SignalNameOther}`)
  + use a parsing tool to decode the input expression.
  + insert the key-value (varname: resource) in the global environment.
  + resource is a Signal.
  + might have call some function to fetch the resource
    + So expose a callback that shall be used to fetch the resource. This can be set in the user-app
    + The callback parameters could be time, data, units, ....
    + The processor will create a `Signal` object for each of the variable name i.e, the words in `${}`.
    + We do not make any call to get the data. That is part of iplotDataAccess.
    + You are only required to provide a callback that will initialize a resource for a signal
  + now eval the expression. `core/Signal` has implementations for every mathematical operation
        and other complex stuff too(`__getitem__`). So ${Sig1} + ${Sig2} evaluates correctly in python.
  + will initialize a couple keys in our local environment.
    + `time`: the time base. (`Signal.time`)
    + `data`: the ydata in case of 1D signals. (`Signal.data`)
    + `data_primary`: alias for data. (`Signal.data_primary`)
    + `data_secondary`: the position vector in case of 2D signals. (ex: r in Te = f(r, t)) (`Signal.data_secondary`)
    + `time_unit`: `Signal.time_unit`
    + `data_unit`: `data.unit`
    + `data_primary_unit`: `data_primary.unit`
    + `data_secondary_unit`: `data_secondary.unit`
    + more to come..
    + ....
  + Now, within a processor `${time}` would evaluate to the expression's time base.
  + Similarly `${data}` would evaluate to the expression's data.
  + So on for other local variables
  + What about aliases?