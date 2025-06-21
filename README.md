# bria-internal
internal tools for general use
___

# First time, here's a checklist:

> ### Run:
> * uv pip install pre-commit
> * pre-commit install

> ### Tests:
> * each test file should be placed near its tested file
> * test file name should follow: *_tests.py

> ### adding packages
> common packages that need to be installed every time:
> 
>   > uv add [my-package]
>
> grouped dependencies:
> 
>   > uv add [my-package] --optional all  
>   > uv add [my-package] --optional [my-group]
>   