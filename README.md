# bria-internal
internal tools for general use  
to show pkg versions run: `sh ./scripts/show_releases.sh`
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
> ### Release
> 
>   > change the version in the pyproject.toml  
>   > run the release workflow manually from the ui
>   > preferablly name the commit of the relase as ->   
>   > release: \<release version\>
> 