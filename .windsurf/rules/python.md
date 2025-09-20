---
trigger: glob
globs: *.py
---

NEVER log with print().  Use logger
NEVER use bare excelption handlers.  only use exception handling if you have a VERY specific exception we want to catch
NEVER import inside of classes of funcitons, unless it is ABSOLUTELY necessary
AVOID fallback logic, unless specifically requested
Strive to be effective with code & deliver very few lines of code
ALWAYS stay on task & not go out of scope from the parent response.  if you see things you want to assk tell the user in chat, not code.
