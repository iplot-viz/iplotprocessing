## Structure
```bash
├── common # ParameterID functions, table helpers, exceptions
├── core # core data objects will be managed by a context i.e, user/developer's contact with signal processing methods
├── example # An example demonstrating how everything (context, processors, varnames) fits together. 
├── tests 
└── tools # additional tools that don't fit in core or context
```

+ The context can initialize itself from a pandas DataFrame or a csv file.
+ The delimiter is customizable. Commonly used delimiter is ','. 
+ The ',' delimiter causes a disambiguity when a field has a function with two or more arguments separated by ','
  + Ex: convolve(${self}.time, ones(5))
+ As the table (pd.DataFrame) is read, aliases are registered and new signals are added.
+ An alias can refer to 
  + a data source and a variable name
  + an expression involving one or more variable names
  + an expression involving one or more aliases
+ Aliases can be used before their definition.
+ The implementation makes sure aliases are available prior to addition of new signals.
```bash
|--------------ENVIRONMENT-------------|
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|some_alias: hash(ds, some_varname)    |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|hash(ds, some_varname): Signal        |
|some_alias: hash(ds, some_varname)    |
|some_alias: hash(ds, some_varname)    |
|hash(ds, some_varname): Signal        |
|some_alias: hash(ds, some_varname)    |
|some_alias: hash(ds, some_varname)    |
|some_alias: hash(ds, some_varname)    |
|some_alias: hash(ds, some_varname)    |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|...:...                               |
|--------------------------------------|
```

## Implementation
+ The context will have a global environment
+ The environment
  + is a hash-value dictionary
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
+ The procedure to add a Signal,
  + Context will need a variable name and a data source. 
    + Ex. with codacuda DS, something like `${SignalName-X-Y-Z}+${SignalNameOther}` or simply `SignalName-X-Y-Z`
    + Ex. with imasuda DS, something like `${core_profiles/profiles_1d/j_ohmic} + ${something/similar/to/the/previous/one}` or simply `core_profiles/profiles_1d/j_ohmic`
  + Context uses a parsing tool to decode the input expression.
  + insert the key-value (varname: resource) in the global environment.
    + resource is a Signal.
  + During this stage the environment cannot yet be used to evaluate expressions.
    + The Signal's input expression should contain entries that are hash values (from the environment)
    + At the time of addition, the Signal's input expression is in ASCII format.
    + The parsing tool can interpret keys from its varDict, localDict member.
  + It is required to **build** the context map.
  + The process of building the context map implies that the existing environment must be used in the Signal's input expression.
+ An expression can be evaluated with the context.
  + It might have call some function to fetch the resource
    + So expose a callback that shall be used to fetch the resource. This can be set in the user-app
    + The callback parameters could be time range, pulse number, no. of samples, ...
    + You are only required to provide a callback that will initialize a resource for a signal
  + now eval the expression. `core/Signal` has implementations for every mathematical operation
        and other complex stuff too(`__getitem__`). So ${Sig1} + ${Sig2} evaluates correctly in python.
  + The local environment is setup as a throw-away dictionary for current evaluation.
  + The `evaluate` function will initialize a couple keys in the local environment.
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
    + If the alias was registered, its valid to query an expression containing the alias.
