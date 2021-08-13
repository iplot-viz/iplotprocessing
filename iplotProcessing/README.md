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
        words or numbers inside square-brackets (in case of AoS). Obviously, only the iplotDataAccess module can
        understand it.
  + The value in the dictionary for a given key is a `core/Signal` object
  + We will have to somehow initialize a `core/Signal` object populated with the time, data members prior
        to evaluating the expression.
  + Without deep-copying the iplotDataAccess/dataObj data, since sometimes the data size is in the magnitude of tera bytes..
+ The processor 
  + will have access to the global environment of the context it is registered with.
  + and a local environment for the real data, time, units information. 
  + will need an input expression. 
    + Ex. with codacuda DS, something like `${SignalName-X-Y-Z}+${SignalNameOther}` or simply `SignalName-X-Y-Z`
    + Ex. with imasuda DS, something like `${core_profiles/profiles_1d/j_ohmic} + ${something/similar/to/the/previous/one}` or simply `core_profiles/profiles_1d/j_ohmic`
    + If alias is provided, register the alias globally.
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
    + `time`: the time base. (represented by `Signal.time`)
    + `data`: the ydata in case of 1D signals. (represented by `Signal.data`)
    + `data_primary`: alias for data. (represented by `Signal.data_primary`)
    + `data_secondary`: the position vector in case of 2D signals. (ex: r in Te = f(r, t)) (represented by `Signal.data_secondary`)
    + `time_unit`: represented by `Signal.time_unit`
    + `data_unit`: represented by `data.unit`
    + `data_primary_unit`: represented by `data_primary.unit`
    + `data_secondary_unit`:represented by `data_secondary.unit`
    + more to come..
    + ....
  + Now, within a processor `${time}` would evaluate to the expression's time base.
  + Similarly `${data}` would evaluate to the expression's data.
  + So on for other local variables
  + What about aliases?
  	+ These appear to be names that can be used anywhere in the context and even across processors
    + These will be stored in the global environment and can be used to refer to the `core/Signal` object
    + So, all of these would evaluate correctly accordint the python data-member access syntax
  	  + `${Johm}.time` = The member `time` of the `core/Signal` object registered under the alias Johm in the global environment.
  	  + `(ml0002+ml0004)/1` = The sum of two `core/Signal` objects which are registered under the alias `ml0002` and `ml0004`. 
         Recall that mathematical operations on `core/Signal` objects are performed on the data with proper time mixing/interpolation.
         Since `core/Signal` shall implement `__add__` and other mathematical ops. See [operators](https://docs.python.org/3/library/operator.html)
         for some of the mathematical operators `core/Signal` shall implement. Basic '+', '*', '-', '/', etc.
