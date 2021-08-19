## Structure
```bash
├── core # core data objects will be managed by a context i.e, user/developer's contact with signal processing methods
├── tests 
└── tools # additional tools that don't fit in core or context
```

## ASCII art
+ So far, the information flow looks like this.
```bash

 _______________		 		|--[Input expression] # to initialize the signal. 
|				|<--------------| # For ex. 
|  Processor 	|              # 1. `${SignalName-X-Y-Z}+${SignalNameOther}` or simply `SignalName-X-Y-Z`
|				|			   # 2. `${core_profiles/profiles_1d/j_ohmic} + ${something/similar/to/the/previous/one}` or simply `core_profiles/profiles_1d/j_ohmic`
|---------------|              # 3. Using pre-registered aliases. `(ml0002 + ml0004) / 2` 
       |
       |  # multiple query points. these can be used in the columns of a variables table, axis labels of a plot, title of a plot, in the legend and so on.
       |<-----------------|evaluate(expr)| # for ex, expr = "${Johm}"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "${rtn}"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "${rtn}.time"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "${Johm}.time"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "convolve(time, ones(5), 'valid') / 5"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "time-15s"
       |
       |<-----------------|evaluate(expr)| # for ex, expr = "{Johm}.time_unit" (Ability to use this in axis label format)
       |
       |....
       |
       |..... any number of query points
```

+ So far, the bigger picture looks like this.
+ The context manages the evaluation of the registered processors. Think of auto applying upon change in data or user interaction event.
+ The processors could be designed to recompute upon change but I need to think more about this.
  + register an `evaluate` callback that the UI/dataAccess module shall call with time, data, units parameters upon change
+ Think of the processors to map to specific stack of plots in the variables table.
+ I've tried to map the separation of distinct input expressions in the varname column to different processors.
+ With the use of aliases one could access other processors signal objects and reuse other information (units, etc)
```bash
|---------------------------------------------------------------------------|
|									CONTEXT									|
|---------------------------------------------------------------------------|
| 		ENVIRONMENT						| 			PROCESSORS              |
|										|									|
|		some varname: Signal 			|[Processor-0] <-- Input Expression |
|		some varname: Signal 			|		|<----|evaluate(expr1)		|
|		some varname: Signal 			|		|<----|evaluate(expr2)		|
|		some alias: varname				|		|...						|
|		some varname: Signal			|[Processor-1] <-- Input Expression |
|		some varname: Signal			|		|<----|evaluate(expr1)		|
|		some varname: Signal			|		|<----|evaluate(expr2)		|
|		some varname: Signal			|		|...						|
|		some varname: Signal			|[Processor-2] <-- Input Expression |
|		some varname: Signal			|		|<----|evaluate(expr1)		|
|		some varname: Signal			|		|<----|evaluate(expr2)		|
|		some alias: varname				|		|...						|
|		some alias: varname				|[Processor-3] <-- Input Expression |
|		some varname: Signal			|		|<----|evaluate(expr1)		|
|		some alias: varname				|		|<----|evaluate(expr2)		|
|		some alias: varname				|		|...						|
|		some alias: varname				|[Processor-4] <-- Input Expression |
|		some alias: varname				|		|<----|evaluate(expr1)		|
|		...:... 						|		|<----|evaluate(expr2)		|
|		...:...							|		|...						|
|		...:...							|[Processor-5] <-- Input Expression |
|		...:...							|		|<----|evaluate(expr1)		|
|		...:...							|		|<----|evaluate(expr2)		|
|		...:...							|		|...						|
|		...:...							|[Processor-6]....					|
|		...:...							|...								|
|		...:...							|...								|
|		...:...							|...								|
|		...:...							|									|
|										|									|
|---------------------------------------------------------------------------|
```

## Implementation
+ The context will have one global environment and one or more processors.
+ The environment
  + is a key-value based dictionary of variable names and their data.
  + For example, 
    + considering a codacuda DS, the variable name is a series of alpha-numeric characters
        that the iplotDataAccess module can understand.
    + considering an imasuda DS, the variable name is a forward-slash separated sequence of
        words or numbers inside square-brackets (in case of AoS). Obviously, only the iplotDataAccess module can
        understand it.
  + The value in the dictionary for a given key is a `core/Signal` object
  + We will have to somehow initialize a `core/Signal` object populated with the time, data members prior
        to evaluating the expression.
  + The key must also encode the data-source.
    + Ex: varname=IP1, DS=JET and varname=IP1, DS=codacuda must be unique.
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
  + Now, within a processor `time` would evaluate to the expression's time base.
  + Similarly `data` would evaluate to the expression's data.
  + So on for other local variables
  + What about aliases?
  	+ These appear to be names that can be used anywhere in the context and even across processors
    + These will be stored in the global environment and can be used to refer to the `core/Signal` object
    + `self` in python means the object itself. Similarly, proposed syntax to access the current row's signal's members is
      + Ex: for time access, `${self}.time`
      + Ex: for data access, `${self}.data`
    + So, all of these would evaluate correctly accordint the python data-member access syntax
      + `${self}.time` = The member `time` of the `core/Signal` object for the processor corresponding to current row.
  	  + `${Johm}.time` = The member `time` of the `core/Signal` object registered under the alias Johm in the global environment.
  	  + `(ml0002+ml0004)/1` = The sum of two `core/Signal` objects which are registered under the alias `ml0002` and `ml0004`. 
         Recall that mathematical operations on `core/Signal` objects are performed on the data with proper time mixing/interpolation.
         Since `core/Signal` shall implement `__add__` and other mathematical ops. See [operators](https://docs.python.org/3/library/operator.html)
         for some of the mathematical operators `core/Signal` shall implement. Basic '+', '*', '-', '/', etc.
    + Aliases can be used for querying the processor to evaluate an expression.
    + If the alias was registered, its valid to query an expression containing the alias.
