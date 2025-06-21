# bria-internal
internal tools for general use
___


# First time, here's a checklist:
>### Run:
>* uv pip install pre-commit
>* pre-commit install

>### Tests:
> * each test file should be placed near its tested file
> * test file name should follow: *_tests.py

___



# adding packages

### for common packages that needs to be installed everytime 
    uv add [my-package]

### for grouped dependencies:
    uv add [my-package] --optional all
    uv add [my-package] --optional [my-group]


